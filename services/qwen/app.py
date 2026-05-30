"""
PrepAIred — Qwen Microservice  (port 8001)
==========================================
Auxiliary LLM support for hints, follow-ups, partial evaluation, and reports.

Endpoints:
  POST /hint           → Qwen 1.5B, streaming SSE
  POST /followup       → Qwen 1.5B, streaming SSE
  POST /partial_eval   → Qwen 7B, JSON (ambiguity gate)
  POST /report         → Qwen 7B, streaming SSE

Both models are loaded ONCE at startup and kept warm when available.
Never call this service synchronously from the main backend —
always use async / background tasks.

Run with:
    uvicorn main:app --port 8001 --reload
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import re
import time
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


torch = None
AutoModelForCausalLM = None
AutoTokenizer = None
BitsAndBytesConfig = None
TextIteratorStreamer = None
_ML_IMPORT_LOCK = threading.Lock()


def _ensure_ml_imports():
    """Import heavy ML dependencies lazily to avoid blocking module import/startup."""
    global torch, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextIteratorStreamer
    if torch is not None:
        return
    with _ML_IMPORT_LOCK:
        if torch is not None:
            return
        import torch as _torch
        from transformers import (
            AutoModelForCausalLM as _AutoModelForCausalLM,
            AutoTokenizer as _AutoTokenizer,
            BitsAndBytesConfig as _BitsAndBytesConfig,
            TextIteratorStreamer as _TextIteratorStreamer,
        )
        torch = _torch
        AutoModelForCausalLM = _AutoModelForCausalLM
        AutoTokenizer = _AutoTokenizer
        BitsAndBytesConfig = _BitsAndBytesConfig
        TextIteratorStreamer = _TextIteratorStreamer


# ── Model registry ───────────────────────────────────────────────────────────

class ModelRegistry:
    """Singleton registry — loads both models once, keeps them warm."""

    _instance: Optional["ModelRegistry"] = None

    def __init__(self):
        self.models: dict = {}
        self.tokenizers: dict = {}
        self._lock = asyncio.Lock()
        self.loading: dict[str, bool] = {}
        self.errors: dict[str, str] = {}

    @classmethod
    def get(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = ModelRegistry()
        return cls._instance

    def load_model(self, key: str, model_id: str, use_4bit: bool = True):
        """Load and cache a model by key. Call from startup."""
        if key in self.models:
            return

        _ensure_ml_imports()

        print(f"[QwenService] Loading {key} ({model_id}) …", flush=True)
        t0 = time.time()

        quantization_config = None
        if use_4bit and torch.cuda.is_available():
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )

        device_map = "auto" if torch.cuda.is_available() else "cpu"

        tok = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
            cache_dir=f"models/{key}",
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config,
            device_map=device_map,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True,
            cache_dir=f"models/{key}",
        )
        model.eval()

        self.tokenizers[key] = tok
        self.models[key] = model

        elapsed = time.time() - t0
        print(f"[QwenService] {key} ready in {elapsed:.1f}s", flush=True)

    def generate_stream(self, key: str, prompt: str, max_new_tokens: int = 256):
        """Return a streaming iterator for token-by-token output."""
        _ensure_ml_imports()
        tok = self.tokenizers[key]
        model = self.models[key]

        inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=2048)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)

        gen_kwargs = {
            **inputs,
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "streamer": streamer,
        }

        thread = threading.Thread(target=model.generate, kwargs=gen_kwargs)
        thread.start()
        return streamer

    def generate_full(self, key: str, prompt: str, max_new_tokens: int = 512) -> str:
        """Blocking full-text generation (for JSON responses)."""
        _ensure_ml_imports()
        tok = self.tokenizers[key]
        model = self.models[key]

        inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=3072)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=1.0,
            )

        prompt_len = inputs["input_ids"].shape[1]
        new_tokens = out[0][prompt_len:]
        return tok.decode(new_tokens, skip_special_tokens=True)


# ── App lifespan ─────────────────────────────────────────────────────────────

MOCK_MODE = False   # Set True when running without GPU / models
WARMUP_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="qwen_warmup")
WARMUP_TASK: Optional[asyncio.Task] = None


async def _warm_models_background():
    """Warm both models in background so service can bind immediately."""
    global MOCK_MODE
    registry = ModelRegistry.get()
    loop = asyncio.get_running_loop()
    model_plan = [
        ("qwen_1b", "Qwen/Qwen2.5-1.5B-Instruct", True),
        ("qwen_7b", "Qwen/Qwen2.5-7B-Instruct", True),
    ]
    any_loaded = False

    for key, model_id, use_4bit in model_plan:
        registry.loading[key] = True
        try:
            await loop.run_in_executor(
                WARMUP_EXECUTOR,
                registry.load_model,
                key,
                model_id,
                use_4bit,
            )
            any_loaded = True
            registry.errors.pop(key, None)
        except Exception as exc:
            registry.errors[key] = str(exc)
            print(f"[QwenService] Failed loading {key}: {exc}", flush=True)
        finally:
            registry.loading[key] = False

    if not any_loaded:
        MOCK_MODE = True
        print("[QwenService] No models loaded. MOCK mode enabled.", flush=True)
    else:
        print("[QwenService] Warmup task completed.", flush=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global WARMUP_TASK
    print("[QwenService] Starting service; warming models in background.", flush=True)
    WARMUP_TASK = asyncio.create_task(_warm_models_background())
    yield
    if WARMUP_TASK and not WARMUP_TASK.done():
        WARMUP_TASK.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await WARMUP_TASK
    WARMUP_EXECUTOR.shutdown(wait=False, cancel_futures=True)
    print("[QwenService] Shutting down.", flush=True)


app = FastAPI(title="PrepAIred Qwen Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic request schemas ──────────────────────────────────────────────────

class HintRequest(BaseModel):
    question_text: str
    topic: str
    transcript: str = ""
    difficulty: int = 3
    strong_points: list[str] = []
    missing_concepts: list[str] = []


class FollowupRequest(BaseModel):
    question_text: str
    topic: str
    transcript: str
    strong_points: list[str] = []
    weakest_gap: str = ""
    difficulty: int = 3


class PartialEvalRequest(BaseModel):
    question_text: str
    transcript: str
    mandatory: list[str] = []
    concept_groups: list[list[str]] = []
    s1_score: float = 0.5
    s2_score: float = 0.5
    combined_score: float = 0.5


class ReportRequest(BaseModel):
    candidate_name: str = "Candidate"
    questions: list[dict]       # [{text, topic, difficulty, score, transcript}]
    overall_score: float
    c_score: float
    dsa_score: float
    difficulty_history: list[int] = []
    behaviour: dict = {}


# ── Prompt builders ───────────────────────────────────────────────────────────

def _hint_prompt(req: HintRequest) -> str:
    strong = "\n".join(f"  ✓ {p}" for p in req.strong_points) or "  (none yet)"
    missing = "\n".join(f"  ✗ {m}" for m in req.missing_concepts) or "  (not assessed yet)"
    return f"""You are a supportive technical interview coach.

QUESTION (Difficulty {req.difficulty}/5, Topic: {req.topic}):
{req.question_text}

CANDIDATE'S ANSWER SO FAR:
"{req.transcript or '(no answer yet)'}"

WHAT THEY GOT RIGHT:
{strong}

WHAT THEY MISSED:
{missing}

Give a concise hint (2-3 sentences) that:
1. Acknowledges what they got right (if anything)
2. Nudges toward the core concept they are missing
3. Does NOT give the answer away

Hint:"""


def _followup_prompt(req: FollowupRequest) -> str:
    return f"""You are a sharp technical interviewer probing deeper.

ORIGINAL QUESTION (Topic: {req.topic}):
{req.question_text}

CANDIDATE'S ANSWER:
"{req.transcript}"

THEIR BIGGEST GAP:
{req.weakest_gap or "unclear reasoning"}

Write ONE precise follow-up question that:
1. Directly targets their biggest gap
2. Builds on something they DID say (don't ignore their answer)
3. Is answerable in 60-90 seconds
4. Increases difficulty naturally

Follow-up question:"""


def _partial_eval_prompt(req: PartialEvalRequest) -> str:
    mandatory = "\n".join(f"  - {m}" for m in req.mandatory) or "  (none)"
    groups_str = ""
    for i, g in enumerate(req.concept_groups, 1):
        groups_str += f"  Group {i}: {', '.join(g)}\n"
    groups_str = groups_str or "  (none)"

    return f"""You are an expert technical evaluator. Evaluate this answer carefully.

QUESTION:
{req.question_text}

REQUIRED CONCEPTS (mandatory for full credit):
{mandatory}

CONCEPT GROUPS (partial credit zones):
{groups_str}

CANDIDATE'S ANSWER:
"{req.transcript}"

CURRENT AUTOMATED SCORES:
- Semantic similarity (S1): {req.s1_score:.2f}
- Concept coverage (S2): {req.s2_score:.2f}
- Combined: {req.combined_score:.2f}

The automated scorer flagged this as AMBIGUOUS (S1 high but S2 incomplete).
Your task: provide a deeper evaluation.

Respond ONLY with valid JSON (no markdown, no preamble):
{{
  "rubric_score": <float 0.0-1.0, your assessment of rubric coverage>,
  "qwen_bonus": <float 0.0-0.20, bonus for genuinely correct extra info NOT in rubric>,
  "final_score": <float 0.0-1.0, rubric_score + qwen_bonus, capped at 1.0>,
  "missing_concepts": ["concept the candidate missed", ...],
  "strong_points": ["concept explained well", ...],
  "vague_points": ["concept mentioned but unclear", ...],
  "justification": "1-2 sentence score justification"
}}"""


def _report_prompt(req: ReportRequest) -> str:
    q_summaries = ""
    for i, q in enumerate(req.questions, 1):
        q_summaries += f"\nQ{i} [{q.get('topic','?')} D{q.get('difficulty','?')}]: {q.get('text','')[:120]}\n"
        q_summaries += f"  Score: {q.get('score',0):.0%}  |  Answer excerpt: {str(q.get('transcript',''))[:200]}\n"

    beh = req.behaviour
    return f"""You are writing a post-interview feedback report for {req.candidate_name}.

PERFORMANCE SUMMARY:
- Overall score: {req.overall_score:.0%}
- C Language score: {req.c_score:.0%}
- DSA score: {req.dsa_score:.0%}
- Difficulty reached: {max(req.difficulty_history, default=3)}/5
- Confidence score: {beh.get('avg_confidence', 0.7):.0%}
- Hesitation rate: {beh.get('hesitation_rate', 0.15):.0%}

QUESTION-BY-QUESTION:
{q_summaries}

Write a personalised, encouraging feedback report (3-4 paragraphs) that:
1. Opens with an overall impression (name the candidate)
2. Highlights their 2-3 strongest areas specifically
3. Identifies 2-3 concrete areas to improve with study suggestions
4. Closes with actionable next steps

Be specific to their actual answers. Sound like a senior engineer who genuinely wants them to succeed.

Report:"""


# ── SSE stream helper ─────────────────────────────────────────────────────────

async def _sse_stream(key: str, prompt: str, max_tokens: int, mock_text: str) -> AsyncGenerator[str, None]:
    """Async SSE generator. Falls back to chunked mock in MOCK_MODE."""
    if MOCK_MODE:
        words = mock_text.split()
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'token': chunk})}\n\n"
            await asyncio.sleep(0.03)
        yield "data: [DONE]\n\n"
        return

    registry = ModelRegistry.get()
    if key not in registry.models:
        words = mock_text.split()
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'token': chunk})}\n\n"
            await asyncio.sleep(0.03)
        yield "data: [DONE]\n\n"
        return

    streamer = await asyncio.get_event_loop().run_in_executor(
        None,
        registry.generate_stream,
        key,
        prompt,
        max_tokens,
    )

    for token in streamer:
        if token:
            yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    registry = ModelRegistry.get()
    cuda_available = False
    if torch is not None:
        try:
            cuda_available = bool(torch.cuda.is_available())
        except Exception:
            cuda_available = False
    return {
        "status": "ok",
        "mock_mode": MOCK_MODE,
        "models_loaded": list(registry.models.keys()),
        "models_loading": {k: bool(v) for k, v in registry.loading.items()},
        "model_errors": registry.errors,
        "cuda_available": cuda_available,
    }


@app.post("/hint")
async def generate_hint(req: HintRequest):
    """
    Streaming hint — Qwen 1.5B.
    Client reads SSE stream, each event: {"token": "..."}
    Final event: [DONE]
    """
    prompt = _hint_prompt(req)
    mock = (
        f"You've correctly identified {req.strong_points[0] if req.strong_points else 'part of the answer'}. "
        f"Think about {req.missing_concepts[0] if req.missing_concepts else 'the underlying mechanism'} "
        f"and how it connects to {req.topic}. Consider what happens in the edge case where the input is empty or null."
    )
    return StreamingResponse(
        _sse_stream("qwen_1b", prompt, 128, mock),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/followup")
async def generate_followup(req: FollowupRequest):
    """
    Streaming follow-up question — Qwen 1.5B.
    """
    prompt = _followup_prompt(req)
    mock = (
        f"Interesting — you mentioned {req.transcript.split()[:3] if req.transcript else ['the']} ... "
        f"Can you walk me through what happens to memory when this function returns? "
        f"Specifically, what would change if the input size doubled?"
    )
    return StreamingResponse(
        _sse_stream("qwen_1b", prompt, 96, mock),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/partial_eval")
async def partial_eval(req: PartialEvalRequest):
    """
    Deep partial-credit evaluation — Qwen 7B, returns JSON.
    Only called when automated scorer is ambiguous (S1 > 0.40, S2 < 0.60).

    Returns:
        rubric_score, qwen_bonus, final_score,
        missing_concepts, strong_points, vague_points, justification
    """
    registry = ModelRegistry.get()
    if MOCK_MODE or "qwen_7b" not in registry.models:
        bonus = min(0.08, len(req.transcript.split()) * 0.002)
        return {
            "rubric_score": round(req.combined_score, 3),
            "qwen_bonus": round(bonus, 3),
            "final_score": round(min(1.0, req.combined_score + bonus), 3),
            "missing_concepts": ["Complexity analysis", "Edge case handling"],
            "strong_points": ["Core concept identified"],
            "vague_points": ["Explanation lacks precision"],
            "justification": f"[MOCK] Combined score {req.combined_score:.2f} — partial credit applied.",
        }

    prompt = _partial_eval_prompt(req)
    raw = await asyncio.get_event_loop().run_in_executor(
        None,
        registry.generate_full,
        "qwen_7b",
        prompt,
        384,
    )

    # Parse JSON from Qwen response
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise HTTPException(500, f"Qwen returned non-JSON: {raw[:200]}")

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"JSON parse error: {e}")

    def _clean(val, max_n=4):
        if not isinstance(val, list):
            return []
        return [str(x).strip() for x in val if str(x).strip()][:max_n]

    rubric_score = float(data.get("rubric_score", req.combined_score))
    qwen_bonus = float(data.get("qwen_bonus", 0.0))
    final_score = min(1.0, max(0.0, float(data.get("final_score", rubric_score + qwen_bonus))))

    return {
        "rubric_score": round(rubric_score, 3),
        "qwen_bonus": round(min(qwen_bonus, 0.20), 3),
        "final_score": round(final_score, 3),
        "missing_concepts": _clean(data.get("missing_concepts", [])),
        "strong_points": _clean(data.get("strong_points", [])),
        "vague_points": _clean(data.get("vague_points", [])),
        "justification": str(data.get("justification", "")).strip(),
    }


@app.post("/report")
async def generate_report(req: ReportRequest):
    """
    Streaming personalised feedback report — Qwen 7B.
    Client reads SSE stream and renders tokens as they arrive.
    """
    prompt = _report_prompt(req)
    mock = (
        f"{req.candidate_name}, you showed strong conceptual grounding across the session, "
        f"particularly in areas requiring systematic reasoning. Your overall score of "
        f"{req.overall_score:.0%} reflects solid preparation. "
        f"Your strongest moments came in questions requiring theoretical explanation — "
        f"you clearly understand the 'why' behind the data structures. "
        f"To push further, focus on time/space complexity analysis and edge case handling in code. "
        f"Practice writing C solutions from scratch under time pressure. "
        f"Next steps: complete 2-3 LeetCode mediums per day focusing on {', '.join([q.get('topic','') for q in req.questions[:2]] or ['linked lists', 'DP'])}, "
        f"and review pointer arithmetic with valgrind. You're on the right track."
    )
    return StreamingResponse(
        _sse_stream("qwen_7b", prompt, 512, mock),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
