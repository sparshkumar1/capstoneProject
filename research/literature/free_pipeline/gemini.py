"""Gemini API client restricted to the FREE tier, NON-GROUNDED analysis/verification only.

Hard guards (not overridable from the CLI):
- the ONLY endpoint is models/gemini-3.6-flash:generateContent (no Deep Research, no interactions/agents, no other model);
- NO tools are ever attached: Google Search grounding is intentionally disabled because this workflow must remain free-only (grounded requests can become
  billable). Any request body containing "tools" is refused before it is sent;
- Gemini is an analysis component: callers supply the source text (abstract / extracted passages); it is never used to retrieve literature;
- a hard local cap on calls per UTC day (every attempt counts, including failures) and a minimum interval between calls;
- any billing/payment/precondition response aborts immediately; nothing here enables or requires billing;
- the key is read from GEMINI_API_KEY in the process environment only, sent in a header (never in the URL), and never printed or stored.
Limitation: the API does not tell the caller which billing tier the project is on; free-tier status can only be confirmed in the Google AI Studio console.
"""
import json
import os
import random
import re
import time

import requests

from fp_common import Throttle, ledger, ledger_count, redact, sha256_text

MODEL = "gemini-3.6-flash"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % MODEL
GROUNDING_ENABLED = False
TOTAL_DAILY_CAP = 150         # attempts per UTC day (all statuses)
RUN_CAP = {"n": 0, "max": 120}   # attempts in this process
MIN_INTERVAL_S = 8.0
_thr = Throttle(MIN_INTERVAL_S)
RATE_EVENTS = {"429": 0}


class FreeTierViolation(RuntimeError):
    pass


class BillingRequired(RuntimeError):
    pass


class QuotaExhausted(RuntimeError):
    pass


class NoKey(RuntimeError):
    pass


def _key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        raise NoKey("GEMINI_API_KEY is not set in this process environment (the key is read from the environment only)")
    return k


def build_body(prompt, max_output_tokens=4096, temperature=0.0):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens, "responseMimeType": "application/json"}}
    return body


def _guard(body):
    if MODEL != "gemini-3.6-flash" or not ENDPOINT.endswith("/models/gemini-3.6-flash:generateContent"):
        raise FreeTierViolation("endpoint/model guard tripped")
    if GROUNDING_ENABLED or "tools" in body or "toolConfig" in body:
        raise FreeTierViolation("grounding/tools are disabled: this workflow must remain free-only")


def ask(prompt, max_output_tokens=4096, temperature=0.0):
    """Single non-grounded generateContent call. Returns dict(text, usage, model_version, finish_reason, service_tier)."""
    body = build_body(prompt, max_output_tokens, temperature)
    _guard(body)
    if ledger_count("gemini", ok_only=False) >= TOTAL_DAILY_CAP:
        raise QuotaExhausted("local daily Gemini attempt cap (%d) reached" % TOTAL_DAILY_CAP)
    ph = sha256_text(prompt)[:16]
    headers = {"Content-Type": "application/json", "x-goog-api-key": _key()}
    for attempt in range(3):
        if RUN_CAP["n"] >= RUN_CAP["max"]:
            raise QuotaExhausted("local per-run Gemini call cap (%d) reached" % RUN_CAP["max"])
        RUN_CAP["n"] += 1
        _thr.wait()
        try:
            r = requests.post(ENDPOINT, headers=headers, data=json.dumps(body), timeout=120)
        except requests.RequestException as e:
            ledger("gemini", "plain", "network_error", prompt_sha=ph, err=redact(e))
            time.sleep(3 * (attempt + 1))
            continue
        ledger("gemini", "plain", r.status_code, prompt_sha=ph)
        if r.status_code == 200:
            return _parse(r.json())
        msg = redact(r.text[:600])
        low = msg.lower()
        if "billing" in low or "failed_precondition" in low or "payment" in low:
            raise BillingRequired("Gemini reported a billing/precondition condition (HTTP %s): %s" % (r.status_code, msg))
        if r.status_code == 429:
            RATE_EVENTS["429"] += 1
            if "perday" in low.replace(" ", "").replace("_", "") or "per day" in low:
                raise QuotaExhausted("Gemini free-tier DAILY quota reached (HTTP 429): %s" % msg)
            m = re.search(r'"retryDelay":\s*"(\d+)', r.text)
            time.sleep(min(70, int(m.group(1)) + 2 if m else 20 * (attempt + 1)) + random.uniform(0, 3))
            continue
        if r.status_code in (500, 503):
            time.sleep(5 * (attempt + 1) + random.uniform(0, 2))
            continue
        raise RuntimeError("Gemini HTTP %s: %s" % (r.status_code, msg))
    raise RuntimeError("Gemini: gave up after retries")


def _parse(d):
    c = (d.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in (c.get("content") or {}).get("parts", []))
    if c.get("groundingMetadata"):
        raise FreeTierViolation("response carried groundingMetadata although no tools were requested; aborting")
    return {"text": text, "usage": d.get("usageMetadata") or {}, "model_version": d.get("modelVersion"), "finish_reason": c.get("finishReason"),
            "service_tier": (d.get("usageMetadata") or {}).get("serviceTier")}


def parse_json_loose(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None
