"""Semantic Scholar Academic Graph API client (free). Unauthenticated access uses a shared pool and can return 429; an optional free
SEMANTIC_SCHOLAR_API_KEY (environment only) raises the limit. Responses are cached on disk so reruns do not repeat calls."""
import json
import os
import random
import time

import requests

from fp_common import CACHE, Throttle, ledger, redact, sha256_text

BASE = "https://api.semanticscholar.org"
FIELDS = ("paperId,title,abstract,year,venue,authors,externalIds,url,citationCount,influentialCitationCount,"
          "openAccessPdf,isOpenAccess,tldr,publicationTypes")
_thr = Throttle(1.2 if os.environ.get("SEMANTIC_SCHOLAR_API_KEY") else 3.2)   # unauthenticated pool is shared: be conservative
RATE_EVENTS = {"429": 0, "retries": 0, "gave_up": 0}
MAX_ATTEMPTS = 4          # per request; identical requests are never repeated beyond this and successes are cached
BREAKER_LIMIT = 4         # consecutive give-ups before the stage aborts (persistent rate limiting is reported, not brute-forced)
_consec = {"n": 0}


class S2Unavailable(RuntimeError):
    """One request gave up after bounded retries."""


class S2Persistent(RuntimeError):
    """Circuit breaker: several consecutive requests gave up; stop and report instead of hammering the shared pool."""


def _get(path, params, use_cache=True):
    key = sha256_text(path + json.dumps(params, sort_keys=True))
    cf = CACHE / "s2" / (key + ".json")
    if use_cache and cf.exists():
        return json.loads(cf.read_text(encoding="utf-8")), True
    headers = {"Accept": "application/json"}
    if os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = os.environ["SEMANTIC_SCHOLAR_API_KEY"]   # header only, never logged
    if _consec["n"] >= BREAKER_LIMIT:
        raise S2Persistent("Semantic Scholar persistently rate limited (%d consecutive give-ups); stopping this stage" % _consec["n"])
    last = None
    for attempt in range(MAX_ATTEMPTS):
        _thr.wait()
        try:
            r = requests.get(BASE + path, params=params, headers=headers, timeout=40)
        except requests.RequestException as e:
            last = redact(e)
            ledger("semanticscholar", "graph", "network_error", path=path.split("?")[0], err=last)
            time.sleep(2 * (attempt + 1) + random.uniform(0, 2))
            RATE_EVENTS["retries"] += 1
            continue
        ledger("semanticscholar", "graph", r.status_code, path=path.split("?")[0])
        if r.status_code == 200:
            data = r.json()
            cf.parent.mkdir(parents=True, exist_ok=True)
            cf.write_text(json.dumps(data), encoding="utf-8")
            _consec["n"] = 0
            return data, False
        if r.status_code in (429, 500, 502, 503, 504):
            RATE_EVENTS["429" if r.status_code == 429 else "retries"] += 1
            ra = r.headers.get("Retry-After")
            try:
                wait = float(ra) if ra else min(90.0, 8.0 * 2 ** attempt)
            except ValueError:
                wait = min(90.0, 8.0 * 2 ** attempt)
            if attempt < MAX_ATTEMPTS - 1:      # no pointless sleep after the final attempt
                time.sleep(min(wait, 120.0) + random.uniform(0, 3))      # exponential backoff with jitter; Retry-After honoured
            continue
        raise RuntimeError("Semantic Scholar HTTP %s: %s" % (r.status_code, redact(r.text[:300])))
    RATE_EVENTS["gave_up"] += 1
    _consec["n"] += 1
    raise S2Unavailable("Semantic Scholar: gave up after %d attempts (%s)" % (MAX_ATTEMPTS, last or "rate limited"))


def search(query, limit=25, offset=0, year_from=None):
    p = {"query": query, "limit": min(limit, 100), "offset": offset, "fields": FIELDS}
    if year_from:
        p["year"] = "%d-" % year_from
    d, cached = _get("/graph/v1/paper/search", p)
    return d.get("data") or [], d.get("total"), cached


def references(paper_id, limit=30):
    d, _ = _get("/graph/v1/paper/%s/references" % paper_id, {"fields": FIELDS, "limit": limit})
    return [x["citedPaper"] for x in d.get("data", []) if x.get("citedPaper") and x["citedPaper"].get("paperId")]


def citations(paper_id, limit=30):
    d, _ = _get("/graph/v1/paper/%s/citations" % paper_id, {"fields": FIELDS, "limit": limit})
    return [x["citingPaper"] for x in d.get("data", []) if x.get("citingPaper") and x["citingPaper"].get("paperId")]


def recommendations(paper_id, limit=20):
    d, _ = _get("/recommendations/v1/papers/forpaper/%s" % paper_id, {"fields": FIELDS, "limit": limit})
    return d.get("recommendedPapers") or []


def normalise(p, query, via):
    ext = p.get("externalIds") or {}
    oa = p.get("openAccessPdf") or {}
    return {
        "s2_id": p.get("paperId"), "title": (p.get("title") or "").strip(), "authors": "; ".join(a.get("name", "") for a in (p.get("authors") or [])),
        "year": p.get("year"), "venue": p.get("venue") or "", "doi": ext.get("DOI") or "", "arxiv": ext.get("ArXiv") or "",
        "url": p.get("url") or "", "abstract": (p.get("abstract") or "").strip(), "citation_count": p.get("citationCount"),
        "influential_citations": p.get("influentialCitationCount"), "oa_pdf_url": oa.get("url") or "", "is_open_access": p.get("isOpenAccess"),
        "tldr": ((p.get("tldr") or {}).get("text") or ""), "found_by": [query], "found_via": [via],
    }
