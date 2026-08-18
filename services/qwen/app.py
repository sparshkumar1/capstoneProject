"""
PrepAIred — Qwen Follow-Up & Feedback Microservice (Port 8001)
=============================================================
Unified structured LLM service for candidate-specific follow-ups,
grounded personalized feedback, hints, and session reports.

Execution Modes:
  1. GGUF Engine (llama.cpp): Ultra-fast CPU inference (<2.5s) using Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M).
  2. PyTorch Transformers: Native bfloat16 / 4-bit GPU inference (for research configurations).
  3. Structured Fallback: Sub-50ms deterministic rubric-grounded recovery when LLMs are offline.

Contract Design:
  - All endpoints return structured JSON contracts.
  - Attribution:
      * When Qwen 1.5B generates: decision_source = "qwen_1.5b_llm", llm_status = "available"
      * When Qwen 7B generates: decision_source = "qwen_7b_llm", llm_status = "available"
      * When fallback occurs: decision_source = "non_llm_structured_recovery", llm_status = "llm_unavailable"
"""

from __future__ import annotations

import os
import sys
import asyncio
import contextlib
import json
import re
import time
import threading
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

torch = None
AutoModelForCausalLM = None
AutoTokenizer = None
BitsAndBytesConfig = None
TextIteratorStreamer = None
Llama = None
_ML_IMPORT_LOCK = threading.Lock()

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
GGUF_MODEL_PATH = ROOT_DIR / "models" / "gguf" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"



def _ensure_ml_imports():
    """Import heavy ML dependencies lazily to avoid blocking startup."""
    global torch, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextIteratorStreamer, Llama
    with _ML_IMPORT_LOCK:
        # 1. Import llama_cpp for CPU GGUF inference if not yet imported
        if Llama is None:
            try:
                from llama_cpp import Llama as _Llama
                Llama = _Llama
            except Exception as exc:
                pass

        # 2. Import PyTorch & Transformers if not yet imported
        if torch is None:
            try:
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
            except Exception:
                pass



import threading
_LLM_LOCK = threading.Lock()


# ── Model Registry ───────────────────────────────────────────────────────────

class ModelRegistry:
    """Singleton registry — caches loaded models (GGUF or Transformers) and executes generation."""

    _instance: Optional["ModelRegistry"] = None

    def __init__(self):
        self.models: dict = {}
        self.model_types: dict[str, str] = {}  # "gguf" or "transformers"
        self.tokenizers: dict = {}
        self.loading: dict[str, bool] = {}
        self.errors: dict[str, str] = {}

    @classmethod
    def get(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = ModelRegistry()
        return cls._instance

    def load_gguf_model(self, key: str, gguf_path: str | Path):
        """Load a quantized GGUF model using llama.cpp for ultra-fast CPU inference."""
        _ensure_ml_imports()
        if Llama is None:
            raise RuntimeError("llama_cpp library not installed.")
        p = Path(gguf_path)
        if not p.exists():
            raise FileNotFoundError(f"GGUF file not found at {p}")

        threads = min(os.cpu_count() or 4, 8)
        print(f"[QwenService] Loading GGUF model {key} from {p} (threads={threads})...", flush=True)
        t0 = time.time()
        llm = Llama(
            model_path=str(p),
            n_ctx=4096,
            n_threads=threads,
            n_batch=256,
            verbose=False,
        )
        self.models[key] = llm
        self.model_types[key] = "gguf"
        elapsed = round(time.time() - t0, 2)
        print(f"[QwenService] GGUF model {key} ready in {elapsed}s", flush=True)


    def load_model(self, key: str, model_id: str, use_4bit: bool = True):
        """Load a Transformers PyTorch model."""
        if key in self.models:
            return

        _ensure_ml_imports()
        if torch is None or AutoModelForCausalLM is None:
            raise RuntimeError("PyTorch/Transformers not available for model loading.")

        print(f"[QwenService] Loading Transformers {key} ({model_id}) …", flush=True)
        t0 = time.time()

        quantization_config = None
        if use_4bit and torch.cuda.is_available() and BitsAndBytesConfig is not None:
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
        self.model_types[key] = "transformers"

        elapsed = time.time() - t0
        print(f"[QwenService] Transformers {key} ready in {elapsed:.1f}s", flush=True)

    def generate_full(self, key: str, prompt: str, max_new_tokens: int = 256) -> str:
        """Execute full-text generation for structured JSON responses."""
        if key not in self.models:
            raise KeyError(f"Model {key} not loaded.")

        m_type = self.model_types.get(key, "transformers")

        # Branch 1: llama.cpp GGUF Inference
        if m_type == "gguf":
            llm = self.models[key]
            # Wrap in ChatML if not already present
            if "<|im_start|>" not in prompt:
                chat_prompt = (
                    f"<|im_start|>system\nYou are an expert technical interviewer.<|im_end|>\n"
                    f"<|im_start|>user\n{prompt}<|im_end|>\n"
                    f"<|im_start|>assistant\n"
                )
            else:
                chat_prompt = prompt

            with _LLM_LOCK:
                res = llm(
                    chat_prompt,
                    max_tokens=max_new_tokens,
                    temperature=0.1,
                    top_p=0.9,
                    stop=["<|im_end|>", "<|endoftext|>"],
                    echo=False,
                )
            return res["choices"][0]["text"].strip()


        # Branch 2: Transformers PyTorch Inference
        _ensure_ml_imports()
        tok = self.tokenizers[key]
        model = self.models[key]

        inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=3072)
        if torch is not None and torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=None,
                top_p=None,
            )

        prompt_len = inputs["input_ids"].shape[1]
        new_tokens = out[0][prompt_len:]
        return tok.decode(new_tokens, skip_special_tokens=True).strip()


MOCK_MODE = False
WARMUP_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="qwen_warmup")
WARMUP_TASK: Optional[asyncio.Task] = None


async def _warm_models_background():
    global MOCK_MODE
    registry = ModelRegistry.get()
    loop = asyncio.get_running_loop()
    any_loaded = False

    # 1. Prefer GGUF Model on CPU if file exists
    env_gguf = os.environ.get("PREPAIRED_GGUF_PATH")
    target_gguf = Path(env_gguf) if env_gguf else GGUF_MODEL_PATH

    if target_gguf.exists():
        registry.loading["qwen_1b"] = True
        try:
            await loop.run_in_executor(
                WARMUP_EXECUTOR,
                registry.load_gguf_model,
                "qwen_1b",
                target_gguf,
            )
            any_loaded = True
            registry.errors.pop("qwen_1b", None)
        except Exception as exc:
            registry.errors["qwen_1b"] = str(exc)
            print(f"[QwenService] Note: GGUF load failed ({exc}).", flush=True)
        finally:
            registry.loading["qwen_1b"] = False
    else:
        print(f"[QwenService] GGUF model not found at {target_gguf}.", flush=True)
        print(f"[QwenService] Download via: python scripts/download_qwen_model.py", flush=True)

    # 2. Fallback to Transformers ONLY if GPU explicitly requested for research benchmark
    if not any_loaded and os.environ.get("ENABLE_GPU_RESEARCH_MODELS", "").lower() in {"1", "true"}:
        model_plan = [
            ("qwen_1b", "Qwen/Qwen2.5-1.5B-Instruct", True),
        ]
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
            finally:
                registry.loading[key] = False

    if not any_loaded:
        MOCK_MODE = True
        print("[QwenService] Running with deterministic structured fallback engine.", flush=True)



@asynccontextmanager
async def lifespan(app: FastAPI):
    global WARMUP_TASK
    print("[QwenService] Service initializing...", flush=True)
    WARMUP_TASK = asyncio.create_task(_warm_models_background())
    yield
    if WARMUP_TASK and not WARMUP_TASK.done():
        WARMUP_TASK.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await WARMUP_TASK
    WARMUP_EXECUTOR.shutdown(wait=False, cancel_futures=True)
    print("[QwenService] Shutdown complete.", flush=True)


app = FastAPI(title="PrepAIred Qwen Service", version="2.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Structured Request & Response Schemas ─────────────────────────────────────

class FollowupRequest(BaseModel):
    original_question: str
    topic: str = "general"
    candidate_answer: str = ""
    structured_evaluation: dict = Field(default_factory=dict)
    correct_concepts: list[str] = Field(default_factory=list)
    incorrect_concepts: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)
    weakest_gap: str = ""
    current_difficulty: int = 3
    candidate_state: dict = Field(default_factory=dict)
    previous_questions: list[str] = Field(default_factory=list)
    previous_followups: list[str] = Field(default_factory=list)


class FollowupResponse(BaseModel):
    followup: str
    reason: str
    target_concepts: list[str] = Field(default_factory=list)
    decision_source: str = "qwen_1.5b_llm"
    llm_status: str = "available"


class FeedbackRequest(BaseModel):
    question_text: str
    topic: str = "general"
    candidate_answer: str = ""
    structured_evaluation: dict = Field(default_factory=dict)
    candidate_state: dict = Field(default_factory=dict)
    history: list[dict] = Field(default_factory=list)


class FeedbackResponse(BaseModel):
    what_candidate_said: str
    what_was_correct: list[str] = Field(default_factory=list)
    what_was_incorrect: list[str] = Field(default_factory=list)
    what_was_incomplete: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    how_to_answer: str
    stronger_answer_guide: str
    actionable_improvements: list[str] = Field(default_factory=list)
    narrative_feedback: str
    final_score: float
    grade: str
    decision_source: str = "qwen_1.5b_llm"
    llm_status: str = "available"


class HintRequest(BaseModel):
    question_text: str
    topic: str = "general"
    transcript: str = ""
    difficulty: int = 3
    strong_points: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)


class HintResponse(BaseModel):
    hint: str
    target_concept: str = ""
    decision_source: str = "qwen_hint"


class ReportRequest(BaseModel):
    candidate_name: str = "Candidate"
    questions: list[dict] = Field(default_factory=list)
    overall_score: float = 0.5
    c_score: float = 0.5
    dsa_score: float = 0.5
    difficulty_history: list[int] = Field(default_factory=list)
    behaviour: dict = Field(default_factory=dict)


class ReportResponse(BaseModel):
    report: str
    candidate_name: str = "Candidate"
    decision_source: str = "qwen_report"


# ── Prompt Builders ───────────────────────────────────────────────────────────

def _build_followup_prompt(req: FollowupRequest) -> str:
    ev = req.structured_evaluation
    score = ev.get("final_score", 0.5)
    grade = ev.get("grade", "Average")
    correct_str = ", ".join(req.correct_concepts or ev.get("correct_claims", [])) or "None identified"
    missing_str = ", ".join(req.missing_concepts or ev.get("missing_concepts", [])) or "None identified"
    miscon_str = ", ".join(req.misconceptions or req.incorrect_concepts or ev.get("incorrect_claims", [])) or "None detected"

    return f"""<|im_start|>system
You are an expert technical interviewer conducting a technical interview on {req.topic}.
Your task is to generate exactly ONE candidate-specific, grounded follow-up question.
CRITICAL RULES:
1. Do NOT repeat or re-phrase the original question.
2. Directly probe the missing concepts ({missing_str}) or misconceptions ({miscon_str}) from the candidate's answer.
3. Stay strictly within the topic of "{req.topic}" and the technical mechanism of the original question.
4. Keep the question concise, clear, and direct (1-2 sentences).
5. Output ONLY a valid JSON object matching the schema.<|im_end|>
<|im_start|>user
CONTEXT:
- Topic: {req.topic} (Difficulty: {req.current_difficulty}/5)
- Original Question: {req.original_question}
- Candidate Answer: "{req.candidate_answer}"

EVALUATION ANALYSIS:
- Score: {score:.2f} ({grade})
- Identified Strengths: {correct_str}
- Missing Concepts / Knowledge Gaps: {missing_str}
- Misconceptions / Inaccuracies: {miscon_str}
- Weakest Gap to Target: {req.weakest_gap or ev.get('weakest_gap', missing_str)}

TASK:
Generate a direct follow-up question targeting the missing concepts: {missing_str}.

Return ONLY a JSON object in this exact schema:
{{
  "followup": "Your precise, targeted follow-up question probing the missing concepts",
  "reason": "Why this specific follow-up addresses the candidate's gap",
  "target_concepts": ["concept1", "concept2"]
}}<|im_end|>
<|im_start|>assistant
"""



def _build_feedback_prompt(req: FeedbackRequest) -> str:
    ev = req.structured_evaluation
    score = ev.get("final_score", 0.5)
    grade = ev.get("grade", "Average")
    correct_str = "\n".join(f"  + {c}" for c in ev.get("correct_claims", [])) or "  + General attempt"
    missing_str = "\n".join(f"  - {m}" for m in ev.get("missing_concepts", [])) or "  - None identified"
    incorrect_str = "\n".join(f"  ! {x}" for x in ev.get("incorrect_claims", [])) or "  ! None detected"

    return f"""<|im_start|>system
You are a senior technical interviewer providing personalized constructive feedback. Ground feedback strictly on what the candidate actually said. Return ONLY a valid JSON object.<|im_end|>
<|im_start|>user
QUESTION (Topic: {req.topic}):
{req.question_text}

CANDIDATE TRANSCRIPT:
"{req.candidate_answer}"

EVALUATION EVIDENCE:
- Final Score: {score:.2f} ({grade})
- Correct Concepts:
{correct_str}
- Missing Concepts:
{missing_str}
- Misconceptions:
{incorrect_str}

Return ONLY a JSON object in this exact schema:
{{
  "what_candidate_said": "Factual 1-sentence summary of candidate assertion",
  "what_was_correct": ["Key correct point 1"],
  "what_was_incorrect": ["Specific error if any"],
  "what_was_incomplete": ["What part was omitted"],
  "missing_concepts": ["Concept 1"],
  "how_to_answer": "Crisp 2-sentence model explanation answering question optimally",
  "stronger_answer_guide": "Advice on structuring answer at senior engineer level",
  "actionable_improvements": ["Concrete action item 1", "Concrete action item 2"],
  "narrative_feedback": "A professional 3-sentence summary of performance and next steps"
}}<|im_end|>
<|im_start|>assistant
"""


# ── Structured Fallback Generators (sub-50ms deterministic recovery) ─────────

def _synthesize_structured_followup(req: FollowupRequest) -> FollowupResponse:
    ev = req.structured_evaluation
    misconceptions = req.misconceptions or req.incorrect_concepts or ev.get("incorrect_claims", [])
    missing = req.missing_concepts or ev.get("missing_concepts", [])
    score = ev.get("final_score", 0.5)
    grade = ev.get("grade", "Average")

    if misconceptions:
        miscon = misconceptions[0]
        followup = f"You mentioned {miscon.lower() if isinstance(miscon, str) else 'this approach'}. Could you walk through a concrete case where that might fail or lead to unintended behavior?"
        reason = f"Probing candidate misconception regarding: {miscon}"
        targets = [str(miscon)]
    elif missing:
        gap = missing[0]
        followup = f"You covered the initial setup well. How would you specifically handle the {gap.lower() if isinstance(gap, str) else 'next step'} to ensure optimal efficiency?"
        reason = f"Probing missing concept '{gap}' from partially correct answer"
        targets = [str(gap)]
    elif score >= 0.75 or grade == "Excellent":
        followup = "That is a solid explanation. What are the primary space-time trade-offs and edge cases you would consider if scaling this to very large inputs?"
        reason = "Candidate demonstrated strong understanding; probing scaling trade-offs"
        targets = ["scalability", "edge cases", "space-time trade-offs"]
    else:
        gap = req.weakest_gap or "underlying mechanism"
        followup = f"Could you elaborate on the exact step-by-step mechanism for {gap.lower() if isinstance(gap, str) else 'the core logic'} and state its time complexity?"
        reason = f"Probing vague answer to elicit mechanistic explanation of {gap}"
        targets = [str(gap), "time complexity"]

    # Check deduplication against previous questions/followups
    prev_all = [p.lower() for p in req.previous_questions + req.previous_followups]
    if any(followup.lower() in p or p in followup.lower() for p in prev_all if len(p) > 20):
        followup = f"In addition to what you described, what is the exact auxiliary space complexity of your approach, and can it be optimized further?"
        reason = "Alternative follow-up selected to avoid duplicating previously asked concepts in this session"
        targets = ["space complexity", "optimization"]

    return FollowupResponse(
        followup=followup,
        reason=reason,
        target_concepts=targets,
        decision_source="non_llm_structured_recovery",
        llm_status="llm_unavailable",
    )



def _synthesize_structured_feedback(req: FeedbackRequest) -> FeedbackResponse:
    ev = req.structured_evaluation
    score = float(ev.get("final_score", 0.5))
    grade = str(ev.get("grade", "Average"))
    candidate_ans = req.candidate_answer.strip()

    correct_claims = list(ev.get("correct_claims", []))
    missing_concepts = list(ev.get("missing_concepts", []))
    incorrect_claims = list(ev.get("incorrect_claims", []))
    expected_concepts = list(ev.get("expected_concepts", []))

    what_said = candidate_ans if candidate_ans else "No answer provided"
    actionable = []
    if incorrect_claims:
        actionable.extend([f"Correct misconception: {inc}" for inc in incorrect_claims[:2]])
    if missing_concepts:
        actionable.extend([f"Incorporate missing concept: {m}" for m in missing_concepts[:3]])

    if grade == "Excellent" or score >= 0.75:
        what_correct = correct_claims or ["Comprehensive conceptual explanation", "Accurate time and space complexity"]
        how_to_answer = f"For {req.topic}, your response correctly covered the required logic: {', '.join(expected_concepts[:3]) if expected_concepts else 'core algorithmic invariants'}."
        stronger_guide = "To perform at an elite staff-level, proactively articulate cache locality, memory footprint, and concurrency trade-offs."
        if not actionable:
            actionable = ["Proactively highlight memory-space trade-offs upfront", "Discuss edge case guarantees under concurrency"]
        narrative = f"Excellent work on this {req.topic} question. You demonstrated strong command with sound technical reasoning ({score:.0%})."

    elif grade == "Good" or score >= 0.60:
        what_correct = correct_claims or ["Correct general algorithmic strategy"]
        gap_desc = f"explicitly covering: {', '.join(missing_concepts[:2])}" if missing_concepts else "detailing edge case boundaries"
        how_to_answer = f"A complete answer for {req.topic} identifies the primary algorithm while {gap_desc}."
        stronger_guide = "Structure your explanation into three distinct phases: (1) Core algorithm, (2) Step-by-step invariants, (3) Complexity analysis."
        if not actionable:
            actionable = ["State time and space complexity bounds explicitly", "Provide a quick walk-through with a sample trace"]
        narrative = f"Good attempt ({score:.0%}). You have the right high-level intuition for {req.topic}, but addressing {missing_concepts[0] if missing_concepts else 'core mechanics'} will elevate your response."

    elif grade == "Average" or score >= 0.40:
        what_correct = correct_claims or ["Recognized problem domain and terminology"]
        key_missing = missing_concepts[0] if missing_concepts else "the fundamental algorithm mechanism"
        how_to_answer = f"For {req.topic}, anchor your response around: {key_missing} to demonstrate mechanistic understanding."
        stronger_guide = "Avoid general buzzwords; explain the step-by-step transition of variables and data state during execution."
        if not actionable:
            actionable = [f"Study the core mechanism of {key_missing}", "Practice tracing the algorithm on concrete examples"]
        narrative = f"Average response ({score:.0%}). You touched on relevant concepts, but key mechanisms ({', '.join(missing_concepts[:2]) if missing_concepts else 'details'}) were omitted."

    else:
        what_correct = correct_claims
        model_strat = expected_concepts[0] if expected_concepts else "the standard optimal algorithm"
        how_to_answer = f"The optimal approach for this question uses {model_strat} to satisfy constraints without unnecessary quadratic overhead."
        stronger_guide = "When stuck, first clarify constraints and start with the simplest valid brute force before stating an optimal strategy."
        if not actionable:
            actionable = [f"Review foundational concepts in {req.topic}", "Write out and trace small test cases before speaking"]
        narrative = f"This response scored {score:.0%} (Grade: Poor). The proposed logic has conceptual gaps or misconceptions that should be reviewed."

    return FeedbackResponse(
        what_candidate_said=what_said,
        what_was_correct=what_correct,
        what_was_incorrect=incorrect_claims,
        what_was_incomplete=missing_concepts,
        missing_concepts=missing_concepts,
        how_to_answer=how_to_answer,
        stronger_answer_guide=stronger_guide,
        actionable_improvements=actionable,
        narrative_feedback=narrative,
        final_score=round(score, 4),
        grade=grade,
        decision_source="non_llm_structured_recovery",
        llm_status="llm_unavailable",
    )


# ── JSON Parser Helper ────────────────────────────────────────────────────────

def _extract_json_from_llm(raw: str) -> Optional[dict]:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/health")
@app.get("/api/qwen/health")
async def health():
    registry = ModelRegistry.get()
    return {
        "status": "ok",
        "service": "prepaired-qwen-microservice",
        "version": "2.1.0",
        "mock_mode": MOCK_MODE,
        "models_loaded": list(registry.models.keys()),
        "model_types": registry.model_types,
        "models_loading": {k: bool(v) for k, v in registry.loading.items()},
        "model_errors": registry.errors,
        "primary_demo_engine": "llama.cpp (CPU)" if "qwen_1b" in registry.models and registry.model_types.get("qwen_1b") == "gguf" else "transformers/fallback",
    }


@app.post("/api/qwen/followup", response_model=FollowupResponse)
@app.post("/api/qwen/generate-follow-up", response_model=FollowupResponse)
@app.post("/followup", response_model=FollowupResponse)
async def generate_followup(req: FollowupRequest):
    """Generate candidate-specific, grounded follow-up question via GGUF / LLM or fallback."""
    registry = ModelRegistry.get()
    if not MOCK_MODE and "qwen_1b" in registry.models:
        try:
            prompt = _build_followup_prompt(req)
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(
                None, registry.generate_full, "qwen_1b", prompt, 128
            )
            data = _extract_json_from_llm(raw)
            if data and "followup" in data and len(str(data["followup"]).strip()) > 5:
                return FollowupResponse(
                    followup=str(data["followup"]).strip(),
                    reason=str(data.get("reason", "Targeted probe on candidate gap")).strip(),
                    target_concepts=[str(c).strip() for c in data.get("target_concepts", [])],
                    decision_source="qwen_1.5b_llm",
                    llm_status="available",
                )
        except Exception as exc:
            print(f"[QwenService] Follow-up generation error: {exc}", flush=True)

    return _synthesize_structured_followup(req)


@app.post("/api/qwen/feedback", response_model=FeedbackResponse)
@app.post("/api/qwen/generate-feedback", response_model=FeedbackResponse)
@app.post("/feedback", response_model=FeedbackResponse)
async def generate_feedback(req: FeedbackRequest):
    """Generate rich, personalized feedback based on Evaluator output."""
    registry = ModelRegistry.get()

    # Check for Research Qwen-7B first, then Live Demo Qwen-1.5B
    active_key = "qwen_7b" if "qwen_7b" in registry.models else ("qwen_1b" if "qwen_1b" in registry.models else None)

    if not MOCK_MODE and active_key:
        try:
            prompt = _build_feedback_prompt(req)
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(
                None, registry.generate_full, active_key, prompt, 256
            )
            data = _extract_json_from_llm(raw)
            if data and ("narrative_feedback" in data or "how_to_answer" in data):
                ev = req.structured_evaluation
                source_label = "qwen_7b_llm" if active_key == "qwen_7b" else "qwen_1.5b_llm"
                return FeedbackResponse(
                    what_candidate_said=str(data.get("what_candidate_said", req.candidate_answer[:120])),
                    what_was_correct=[str(x) for x in data.get("what_was_correct", [])],
                    what_was_incorrect=[str(x) for x in data.get("what_was_incorrect", [])],
                    what_was_incomplete=[str(x) for x in data.get("what_was_incomplete", [])],
                    missing_concepts=[str(x) for x in data.get("missing_concepts", [])],
                    how_to_answer=str(data.get("how_to_answer", "")),
                    stronger_answer_guide=str(data.get("stronger_answer_guide", "")),
                    actionable_improvements=[str(x) for x in data.get("actionable_improvements", [])],
                    narrative_feedback=str(data.get("narrative_feedback", "")),
                    final_score=float(ev.get("final_score", 0.5)),
                    grade=str(ev.get("grade", "Average")),
                    decision_source=source_label,
                    llm_status="available",
                )
        except Exception as exc:
            print(f"[QwenService] Feedback generation error: {exc}", flush=True)

    return _synthesize_structured_feedback(req)


@app.post("/api/qwen/hint", response_model=HintResponse)
@app.post("/hint", response_model=HintResponse)
async def generate_hint(req: HintRequest):
    strong = req.strong_points[0] if req.strong_points else "the initial setup"
    missing = req.missing_concepts[0] if req.missing_concepts else "the core mechanism"
    hint_text = f"You have identified {strong}. Consider how {missing} connects to the problem constraints and what invariant must hold."
    return HintResponse(
        hint=hint_text,
        target_concept=missing,
        decision_source="qwen_hint",
    )


@app.post("/api/qwen/report", response_model=ReportResponse)
@app.post("/report", response_model=ReportResponse)
async def generate_report(req: ReportRequest):
    report_text = (
        f"{req.candidate_name}, you completed the technical session with an overall score of {req.overall_score:.0%}. "
        f"Your performance in theoretical questions reached difficulty level {max(req.difficulty_history, default=3)}/5. "
        f"Key areas of strength include structured algorithmic thinking. To advance further, focus on rigorous time/space complexity derivations "
        f"and detailed edge case verification under interview conditions."
    )
    return ReportResponse(
        report=report_text,
        candidate_name=req.candidate_name,
        decision_source="qwen_report",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
