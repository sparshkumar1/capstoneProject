"""Shared helpers for the free literature pipeline: paths, throttling, API-call ledger, key redaction, title normalisation.
Free-only tooling. No key is ever stored, printed or written to disk; the ledger records status codes and prompt hashes only."""
import datetime as dt
import hashlib
import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
CACHE = STATE / "cache"
LEDGER = STATE / "api_ledger.jsonl"
PAPERS = ROOT / "papers"
VERIF = ROOT / "verification"
ATTACK = ROOT / "attack"


def now_utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def today_utc():
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_text(t):
    return sha256_bytes(t.encode("utf-8"))


_KEY_PATTERNS = [re.compile(r"AIza[0-9A-Za-z_\-]{20,}"), re.compile(r"(?i)(x-goog-api-key|x-api-key)\s*[:=]\s*\S+")]


def redact(text):
    """Scrub anything that looks like an API key, and the exact value of any configured key, from a string."""
    text = str(text)
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "SEMANTIC_SCHOLAR_API_KEY"):
        v = os.environ.get(var)
        if v:
            text = text.replace(v, "[REDACTED]")
    for pat in _KEY_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


def ledger(service, kind, status, **extra):
    """Append one line per API call. Never contains keys or prompt text (prompt hash only)."""
    STATE.mkdir(parents=True, exist_ok=True)
    rec = {"ts": now_utc(), "date_utc": today_utc(), "service": service, "kind": kind, "status": status}
    rec.update({k: (redact(v) if isinstance(v, str) else v) for k, v in extra.items()})
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def ledger_count(service, kind=None, date=None, ok_only=True):
    if not LEDGER.exists():
        return 0
    date = date or today_utc()
    n = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("service") == service and r.get("date_utc") == date and (kind is None or r.get("kind") == kind) \
                and (not ok_only or r.get("status") == 200):
            n += 1
    return n


class Throttle:
    def __init__(self, min_interval_s):
        self.min = min_interval_s
        self.last = 0.0

    def wait(self):
        d = self.min - (time.monotonic() - self.last)
        if d > 0:
            time.sleep(d)
        self.last = time.monotonic()


def norm_title(t):
    t = re.sub(r"[^a-z0-9 ]+", " ", (t or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d
