#!/usr/bin/env python
"""Free literature pipeline for PREPAIred (Semantic Scholar + Gemini 3.6 Flash as a NON-GROUNDED analysis/verification component). See README.md.

Commands:  smoke | selftest | discover | rank | pdfs | verify | attack | matrices        (each accepts --paper 1|2|3 where relevant)
Semantic Scholar is the only retrieval source. Gemini only analyses source text this pipeline supplies (abstract / extracted PDF passages); it never
retrieves literature, never uses Search grounding, and every quote it returns is string-checked locally against the supplied text.
Nothing here calls a paid service or Deep Research, or enables billing (see gemini.py). Frozen research evidence is never read for writing or modified."""
import argparse
import csv
import json
import math
import random
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fp_common as C
import fp_config as CFG
import s2

STATE, VERIF, ATTACK, PAPERS = C.STATE, C.VERIF, C.ATTACK, C.PAPERS
CAND_DIR, CORE_DIR = C.ROOT / "candidates", C.ROOT / "core"
TEXT_DIR = PAPERS / "text"
QUERY_LOG = STATE / "query_log.jsonl"
OVERRIDES = STATE / "manual_screening.json"      # optional human overrides: {"1": {"include": [s2_id], "exclude": [s2_id], "reasons": {s2_id: "..."}}}


# ---------------------------------------------------------------- pool, dedupe
def new_index():
    return {"doi": {}, "s2": {}, "title": {}}


def build_index(pool):
    idx = new_index()
    for k, r in pool.items():
        if r.get("doi"):
            idx["doi"][C.norm_doi(r["doi"])] = k
        if r.get("s2_id"):
            idx["s2"][r["s2_id"]] = k
        idx["title"][C.norm_title(r["title"])] = k
    return idx


def add(pool, idx, rec):
    """Deduplicate on DOI, Semantic Scholar paperId, normalised title (in that order). Returns True if new."""
    if not rec.get("title") or not rec.get("s2_id"):
        return False
    key = idx["doi"].get(C.norm_doi(rec["doi"])) if rec.get("doi") else None
    key = key or idx["s2"].get(rec["s2_id"]) or idx["title"].get(C.norm_title(rec["title"]))
    if key is None:
        key = rec["s2_id"]
        pool[key] = rec
        if rec.get("doi"):
            idx["doi"][C.norm_doi(rec["doi"])] = key
        idx["s2"][rec["s2_id"]] = key
        idx["title"][C.norm_title(rec["title"])] = key
        return True
    old = pool[key]
    for f in ("found_by", "found_via"):
        for v in rec[f]:
            if v not in old[f]:
                old[f].append(v)
    for f in ("abstract", "doi", "oa_pdf_url", "venue", "authors", "arxiv", "tldr", "url"):
        if not old.get(f) and rec.get(f):
            old[f] = rec[f]
    if (rec.get("citation_count") or 0) > (old.get("citation_count") or 0):
        old["citation_count"] = rec["citation_count"]
    old.setdefault("duplicate_ids", [])
    if rec["s2_id"] != old["s2_id"] and rec["s2_id"] not in old["duplicate_ids"]:
        old["duplicate_ids"].append(rec["s2_id"])      # record the merge, never silently replace one version with another
    return False


def load_pool(n):
    f = STATE / ("paper%d_pool.json" % n)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def log_query(**kw):
    QUERY_LOG.parent.mkdir(parents=True, exist_ok=True)
    kw["ts"] = C.now_utc()
    with QUERY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kw, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- ranking and screening scores
def score(n, r):
    """Transparent relevance score. Citation count is a small capped bonus, never the main term."""
    title, absr = r["title"].lower(), (r.get("abstract") or "").lower()
    comps, why, frac = {}, [], {}
    for g, (w, terms) in CFG.PROFILES[n].items():
        ht = [t for t in terms if t in title]
        ha = [t for t in terms if t in absr and t not in ht]
        frac[g] = min(1.0, (2 * len(ht) + len(ha)) / 4.0)
        comps[g] = round(w * frac[g], 3)
        if ht or ha:
            why.append("%s:%s" % (g, "/".join((ht + ha)[:3])))
    rel = sum(comps.values())
    q_hits = len([q for q, v in zip(r["found_by"], r["found_via"]) if v == "search"])
    comps["query_hits"] = round(min(q_hits, 4) * 0.75, 3)
    comps["citations"] = round(min(math.log10(1 + (r.get("citation_count") or 0)), 3) * 0.5, 3)
    comps["expansion"] = 0.5 if any(v != "search" for v in r["found_via"]) else 0.0
    comps["no_abstract_penalty"] = -1.5 if not r.get("abstract") else 0.0
    comps["old_penalty"] = -1.0 if (r.get("year") or 9999) < CFG.YEAR_FROM else 0.0
    comps["_frac"] = {k: round(v, 3) for k, v in frac.items()}
    return round(sum(v for k, v in comps.items() if k != "_frac"), 3), comps, "; ".join(why)


def screening_scores(r, comps):
    """Six 0-3 screening dimensions, derived deterministically from keyword-group coverage and metadata (NOT a quality ranking; no overall score).
    They prioritise which papers are read/verified first."""
    f = comps["_frac"]
    q3 = lambda x: int(min(3, round(3 * x)))
    venue = (r.get("venue") or "").lower()
    peer = bool(r.get("doi")) and venue and "arxiv" not in venue and "corr" != venue
    if peer:
        sq = 3 if (r.get("citation_count") or 0) >= 10 or (r.get("year") or 0) >= 2023 else 2
    elif r.get("arxiv") or "arxiv" in venue or venue == "corr":
        sq = 1
    else:
        sq = 1 if venue else 0
    attack = int(any(v == "attack" for v in r["found_via"]))
    nav = q3((f.get("task", 0) + f.get("method", 0) + f.get("eval", 0)) / 3.0 + 0.34 * attack)
    return {"direct_task_relevance": q3(f.get("task", 0)), "methodological_relevance": q3(f.get("method", 0)), "evaluation_overlap": q3(f.get("eval", 0)),
            "baseline_overlap": q3(f.get("baseline", 0)), "novelty_attack_value": nav, "source_quality": sq}


def ranked(n, pool):
    rows = []
    for k, r in pool.items():
        s, comps, why = score(n, r)
        rows.append(dict(r, score=s, components=comps, why=why, screen=screening_scores(r, comps)))
    rows.sort(key=lambda x: (-x["score"], -(x.get("citation_count") or 0), x["title"]))
    return rows


def load_overrides(n):
    if OVERRIDES.exists():
        return json.loads(OVERRIDES.read_text(encoding="utf-8")).get(str(n), {})
    return {}


def select_core(n, rows):
    """Top-N by transparent relevance score, then documented manual include/exclude overrides. Returns (core_ids, decisions)."""
    tgt = CFG.TARGETS[n]
    ov = load_overrides(n)
    excl, incl, why = set(ov.get("exclude", [])), list(ov.get("include", [])), ov.get("reasons", {})
    cand = rows[:tgt["pool"]]
    auto = [r["s2_id"] for r in cand if r["s2_id"] not in excl][:tgt["core"]]
    core = list(auto)
    for i in incl:
        if i not in core and any(r["s2_id"] == i for r in rows):
            core.append(i)
    dec = {}
    for r in cand:
        i = r["s2_id"]
        if i in excl:
            dec[i] = "excluded manually: " + why.get(i, "no reason recorded")
        elif i in incl:
            dec[i] = "included manually: " + why.get(i, "no reason recorded")
        elif i in auto:
            dec[i] = "selected: top-%d by transparent relevance score" % tgt["core"]
        else:
            dec[i] = "not selected (below core cut-off)"
    return core[:tgt["core"] + len(incl)], dec


# ---------------------------------------------------------------- stages
def cmd_discover(n, expand=True):
    pool = load_pool(n)
    idx = build_index(pool)
    failures = []
    for q in CFG.QUERIES[n]:
        try:
            got, total, cached = s2.search(q, CFG.PER_QUERY_LIMIT, year_from=CFG.YEAR_FROM)
        except s2.S2Unavailable as e:
            print("[P%d] %-70s FAILED (rate limited; will be retried on a later resume)" % (n, q[:70]), flush=True)
            log_query(paper=n, query=q, source="semanticscholar", status="failed", detail=str(e)[:120])
            failures.append(q)
            continue
        except s2.S2Persistent as e:
            print("STOP:", e)
            log_query(paper=n, query=q, source="semanticscholar", status="aborted_persistent_rate_limit")
            failures.append(q)
            break
        new = sum(add(pool, idx, s2.normalise(p, q, "search")) for p in got)
        print("[P%d] %-70s hits=%d new=%d%s" % (n, q[:70], len(got), new, " (cached)" if cached else ""), flush=True)
        log_query(paper=n, query=q, source="semanticscholar", status="ok", hits=len(got), new_unique=new, cached=cached, pool_size=len(pool))
        save_json(STATE / ("paper%d_pool.json" % n), pool)
    if expand and not failures:
        for sd in ranked(n, pool)[:CFG.EXPAND_SEEDS]:
            for via, fn, lim in (("recommendation", s2.recommendations, 20), ("reference", s2.references, 30)):
                try:
                    got = fn(sd["s2_id"], lim)
                except (s2.S2Unavailable, s2.S2Persistent, RuntimeError) as e:
                    print("  expansion skipped (%s): %s" % (via, str(e)[:100]))
                    log_query(paper=n, query="%s of: %s" % (via, sd["title"][:60]), source="semanticscholar", status="failed", detail=str(e)[:100])
                    continue
                new = sum(add(pool, idx, s2.normalise(p, "%s of: %s" % (via, sd["title"][:60]), via)) for p in got)
                print("[P%d] %s of '%s': %d (new %d)" % (n, via, sd["title"][:50], len(got), new), flush=True)
                log_query(paper=n, query="%s of: %s" % (via, sd["title"][:60]), source="semanticscholar", status="ok", hits=len(got), new_unique=new, pool_size=len(pool))
        save_json(STATE / ("paper%d_pool.json" % n), pool)
    print("[P%d] pool size %d; %d queries failed/unretrieved" % (n, len(pool), len(failures)))
    save_json(STATE / ("paper%d_unretrieved.json" % n), {"queries": failures, "ts": C.now_utc()})


def pdf_index():
    f = PAPERS / "PDF_INDEX.csv"
    d = {}
    if f.exists():
        for row in csv.DictReader(f.open(encoding="utf-8")):
            d[row["s2_id"]] = row
    return d


def cmd_rank(n):
    pool = load_pool(n)
    rows = ranked(n, pool)
    tgt = CFG.TARGETS[n]
    core_ids, dec = select_core(n, rows)
    cand = rows[:tgt["pool"]]
    for i in core_ids:               # manual includes may sit outside the candidate cut-off
        if i not in [r["s2_id"] for r in cand]:
            cand.append(next(r for r in rows if r["s2_id"] == i))
    save_json(STATE / ("paper%d_core.json" % n), {"core": core_ids, "ranked_at": C.now_utc(), "decisions": dec})
    ver, pdfs = verification_index(n), pdf_index()
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    out = CAND_DIR / ("PAPER%d_CANDIDATES.csv" % n)
    dims = ["direct_task_relevance", "methodological_relevance", "evaluation_overlap", "baseline_overlap", "novelty_attack_value", "source_quality"]
    cols = ["rank", "is_core", "screening_decision", "relevance_score", "why", "title", "authors", "year", "venue", "doi", "s2_id", "duplicate_s2_ids", "url", "citation_count",
            "oa_pdf_url", "abstract"] + dims + ["source_queries", "found_via", "retrieval_date_utc", "pdf_sha256", "local_pdf", "gemini_verified"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, r in enumerate(cand, 1):
            p = pdfs.get(r["s2_id"], {})
            v = ver.get(r["s2_id"])
            w.writerow([i, r["s2_id"] in core_ids, dec.get(r["s2_id"], ""), r["score"], r["why"], r["title"], r["authors"], r["year"], r["venue"], r["doi"], r["s2_id"],
                        " ".join(r.get("duplicate_ids", [])), r["url"], r["citation_count"], r["oa_pdf_url"], r["abstract"]] + [r["screen"][d] for d in dims] +
                       [" | ".join(r["found_by"]), " | ".join(sorted(set(r["found_via"]))), C.today_utc(), p.get("sha256", ""), p.get("file", ""), bool(v and v[-1].get("status") == "ok")])
    print("[P%d] wrote %s: %d candidates, %d core (pool had %d)" % (n, out.relative_to(C.ROOT), len(cand), len(core_ids), len(pool)))


def core_records(n):
    pool = load_pool(n)
    ids = json.loads((STATE / ("paper%d_core.json" % n)).read_text(encoding="utf-8"))["core"]
    return [pool[i] for i in ids if i in pool]


# ---------------------------------------------------------------- PDFs and text extraction
def extract_text(pdf_path):
    """pypdf text extraction. Returns (text, status). status is 'ok' or a reason the text should not be relied on."""
    try:
        from pypdf import PdfReader
        rd = PdfReader(str(pdf_path))
        parts = []
        for pg in rd.pages[:40]:
            try:
                parts.append(pg.extract_text() or "")
            except Exception:
                parts.append("")
        text = "\n".join(parts)
    except Exception as e:
        return "", "extraction_failed: %s" % type(e).__name__
    letters = sum(ch.isalpha() for ch in text)
    if len(text) < 3000 or letters / max(1, len(text)) < 0.6:
        return text, "extraction_unreliable (chars=%d, alpha_ratio=%.2f)" % (len(text), letters / max(1, len(text)))
    return text, "ok"


def cmd_pdfs(n):
    import requests
    PAPERS.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    idxf = PAPERS / "PDF_INDEX.csv"
    failf = PAPERS / "PDF_UNAVAILABLE.csv"
    have = pdf_index()
    new_file = not idxf.exists()
    cols = ["s2_id", "sha256", "file", "source_url", "doi", "title", "retrieved_utc", "bytes", "text_file", "text_status"]
    for r in core_records(n):
        if r["s2_id"] in have:
            continue
        if not r.get("oa_pdf_url"):
            _note_unavailable(failf, n, r, "no open-access PDF URL in Semantic Scholar metadata")
            continue
        url = r["oa_pdf_url"]
        try:
            resp = requests.get(url, timeout=60, headers={"User-Agent": "PREPAIred-literature-pipeline (academic, open-access only)"})
            body = resp.content
        except requests.RequestException as e:
            print("[P%d] pdf failed %s: %s" % (n, r["title"][:50], C.redact(e)))
            _note_unavailable(failf, n, r, "download error: %s" % type(e).__name__)
            continue
        if resp.status_code != 200 or not body.startswith(b"%PDF") or len(body) > 60_000_000:
            print("[P%d] not a usable PDF (HTTP %s) %s" % (n, resp.status_code, r["title"][:50]))
            _note_unavailable(failf, n, r, "not a usable PDF (HTTP %s)" % resp.status_code)
            continue
        sha = C.sha256_bytes(body)
        path = PAPERS / ("%s__%s.pdf" % (r["s2_id"][:12], sha[:12]))
        if path.exists():      # never overwrite an earlier copy
            continue
        path.write_bytes(body)
        text, tstat = extract_text(path)
        tfile = ""
        if text:
            tp = TEXT_DIR / (path.stem + ".txt")
            tp.write_text(text, encoding="utf-8")
            tfile = tp.name
        with idxf.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(cols)
                new_file = False
            w.writerow([r["s2_id"], sha, path.name, url, r["doi"], r["title"], C.now_utc(), len(body), tfile, tstat])
        print("[P%d] saved %s sha256=%s text=%s" % (n, path.name, sha[:16], tstat), flush=True)
        time.sleep(2)


def _note_unavailable(f, n, r, reason):
    new = not f.exists()
    with f.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["paper", "s2_id", "title", "reason", "ts"])
        w.writerow([n, r["s2_id"], r["title"], reason, C.now_utc()])


# ---------------------------------------------------------------- source-grounded Gemini verification
def norm_q(s):
    """Normalise for quote checking: lowercase, join hyphenated line breaks, keep alphanumerics only, single spaces."""
    s = re.sub(r"-\s*\n\s*", "", (s or "").lower())
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def quote_status(quote, supplied):
    """'verified' only if the (normalised) quote occurs verbatim in the text that was supplied to the model."""
    q = norm_q(quote)
    if len(q) < 12:
        return "no_quote" if not q else "too_short_UNVERIFIED"
    return "verified" if q in norm_q(supplied) else "UNVERIFIED_not_in_supplied_text"


def pick_passages(text, terms, k=4, size=1300):
    """Deterministic local passage selection from extracted PDF text: fixed windows scored by term overlap."""
    if not text:
        return []
    text = re.sub(r"[ \t]+", " ", text)
    wins = [text[i:i + size] for i in range(0, len(text), size - 200)]
    ts = [t.lower() for t in terms]
    scored = sorted(((sum(w.lower().count(t) for t in ts), i, w) for i, w in enumerate(wins)), key=lambda x: (-x[0], x[1]))
    return [(i, w) for s, i, w in scored[:k] if s > 0]


VERIFY_PROMPT = """You are verifying claims about ONE academic paper. Use ONLY the SOURCE TEXT below (metadata, abstract and, if present, passages extracted from the paper).
Do not use memory of the paper, do not infer from the title alone, and never invent methods, numbers, datasets or baselines. If the SOURCE TEXT does not contain the
evidence, use verdict "NOT_DETERMINABLE" and an empty quote. Every non-empty "quote" MUST be copied VERBATIM (<= 35 words) from the SOURCE TEXT.
"basis" must be "SUPPORTED_BY_SOURCE" when a verbatim quote supports the answer, "INFERENCE" when the answer is your inference from the text, or "NONE".

PAPER
Title: {title}
Year: {year}   Venue: {venue}   DOI: {doi}   Semantic Scholar ID: {sid}

SOURCE TEXT
[ABSTRACT] {abstract}
{passages}

OUR CONTRIBUTION CLAIMS (only to judge overlap; they are not facts about this paper)
{claims}

TASK 1 - "extraction": for each of task, method, dataset_environment, baselines, metrics, main_findings give {{"text": "<=40 words", "basis": ..., "quote": ...}}.
TASK 2 - "answers": for each question id give {{"verdict": "YES|NO|PARTIAL|NOT_DETERMINABLE", "text": "<=40 words", "basis": ..., "quote": ...}}.
QUESTIONS
{qs}
TASK 3 - "overlap": for each of our claim ids give {{"relation": "SAME|PARTIAL|BACKGROUND|NONE", "basis": ..., "quote": ...}}, where SAME = this paper's own contribution is
substantially the same, PARTIAL = it does part of it, BACKGROUND = related context only, NONE = unrelated. Judge only from the SOURCE TEXT.

Return ONLY one JSON object: {{"extraction": {{...}}, "answers": {{...}}, "overlap": {{...}}}}."""


def verification_index(n):
    f = VERIF / ("paper%d_verification.jsonl" % n)
    d = {}
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            d.setdefault(r["s2_id"], []).append(r)
    return d


def check_item(item, supplied):
    """Attach quote_check. An item is 'propagated' only if verdict/relation is claimed with a verified quote or is an explicit NOT_DETERMINABLE/NONE."""
    item = dict(item) if isinstance(item, dict) else {}
    item.setdefault("basis", "NONE")
    qc = quote_status(item.get("quote", ""), supplied)
    item["quote_check"] = qc
    verdict = str(item.get("verdict") or item.get("relation") or "").upper()
    neutral = verdict in ("NOT_DETERMINABLE", "NONE", "")
    if qc == "verified" and item["basis"] == "SUPPORTED_BY_SOURCE":
        item["status"] = "SUPPORTED_BY_SOURCE"
    elif neutral and not item.get("quote"):
        item["status"] = "NOT_DETERMINABLE"
    elif qc == "verified":
        item["status"] = "INFERENCE_quote_verified"
    else:
        item["status"] = "UNVERIFIED"          # never propagated into the core matrix
    return item


def cmd_verify(n):
    import gemini as G
    VERIF.mkdir(parents=True, exist_ok=True)
    done = verification_index(n)
    qids = CFG.QUESTION_SETS[n]
    outf = VERIF / ("paper%d_verification.jsonl" % n)
    pdfs = pdf_index()
    claims = "\n".join("%s: %s" % (cid, c) for cid, c in CFG.CONTRIBUTIONS[n])
    terms = sorted({w for q in qids for w in re.findall(r"[a-z]{5,}", CFG.QUESTIONS[q].lower())} |
                   {w for _, c in CFG.CONTRIBUTIONS[n] for w in re.findall(r"[a-z]{6,}", c.lower())})
    for r in core_records(n):
        if r["s2_id"] in done and done[r["s2_id"]][-1].get("status") == "ok":
            continue
        pdf = pdfs.get(r["s2_id"])
        text, passages, basis = "", [], "abstract_only"
        if pdf and pdf.get("text_status") == "ok" and pdf.get("text_file") and (TEXT_DIR / pdf["text_file"]).exists():
            text = (TEXT_DIR / pdf["text_file"]).read_text(encoding="utf-8")
            passages = pick_passages(text, terms)
            basis = "abstract+pdf_passages" if passages else "abstract_only"
        if not r.get("abstract") and not passages:
            rec = {"s2_id": r["s2_id"], "title": r["title"], "ts": C.now_utc(), "status": "skipped_no_source_text", "answers": {}}
        else:
            ptxt = "\n".join("[PASSAGE %d] %s" % (i, w) for i, w in passages)
            supplied = "[ABSTRACT] %s\n%s" % (r["abstract"], ptxt)
            prompt = VERIFY_PROMPT.format(title=r["title"], year=r["year"], venue=r["venue"] or "n/a", doi=r["doi"] or "n/a", sid=r["s2_id"], abstract=r["abstract"] or "(none)",
                                          passages=ptxt, claims=claims, qs="\n".join("%s: %s" % (q, CFG.QUESTIONS[q]) for q in qids))
            try:
                res = G.ask(prompt, max_output_tokens=6000)
            except (G.QuotaExhausted, G.BillingRequired, G.NoKey, G.FreeTierViolation) as e:
                print("STOP:", type(e).__name__, str(e)[:200])
                return
            except RuntimeError as e:
                print("[P%d] Gemini error for %s: %s" % (n, r["title"][:50], C.redact(e)[:160]))
                continue
            parsed = G.parse_json_loose(res["text"]) or {}
            ex = {k: check_item(v, supplied) for k, v in (parsed.get("extraction") or {}).items()}
            an = {q: check_item((parsed.get("answers") or {}).get(q, {}), supplied) for q in qids}
            ov = {cid: check_item((parsed.get("overlap") or {}).get(cid, {}), supplied) for cid, _ in CFG.CONTRIBUTIONS[n]}
            rec = {"s2_id": r["s2_id"], "title": r["title"], "ts": C.now_utc(), "status": "ok" if parsed else "unparsed", "model": res["model_version"] or G.MODEL,
                   "grounded": False, "evidence_basis": basis, "supplied_text_sha256": C.sha256_text(supplied), "supplied_chars": len(supplied),
                   "finish_reason": res["finish_reason"], "extraction": ex, "answers": an, "overlap": ov}
        with outf.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        nun = sum(1 for grp in (rec.get("extraction", {}), rec.get("answers", {}), rec.get("overlap", {})) for v in grp.values() if v.get("status") == "UNVERIFIED")
        print("[P%d] verified: %s (%s, %s, unverified_items=%d)" % (n, r["title"][:55], rec["status"], rec.get("evidence_basis", "-"), nun), flush=True)


# ---------------------------------------------------------------- novelty attack (model proposals; human review required)
ATTACK_PROMPT = """You are helping stress-test a research contribution claim. Judge it ONLY against the papers listed below (title, year, abstract).
Do not use other knowledge; do not assume a paper does something its abstract does not say.

CONTRIBUTION CLAIM: {claim}

CLASSES (provisional, human review required):
RETAIN = none of the listed abstracts describes substantially the same contribution.
NARROW = prior work does part of it; the claim must be restricted to what remains.
REFRAME = the contribution should be presented differently (e.g. as integration, evaluation or decomposition, not as a new method) because similar methods exist.
REMOVE = a listed paper already does substantially the same thing.

LISTED PAPERS
{papers}

Return ONLY JSON: {{"classification": "RETAIN|NARROW|REFRAME|REMOVE", "confidence": "low|medium|high", "rationale": "<=60 words",
"closest": [{{"paper_no": <int>, "basis": "SUPPORTED_BY_SOURCE|INFERENCE", "evidence_quote": "<verbatim quote <=30 words from that paper's abstract>"}}]}}"""


def tok(s):
    return set(re.findall(r"[a-z]{4,}", (s or "").lower()))


def cmd_attack(n):
    import gemini as G
    ATTACK.mkdir(parents=True, exist_ok=True)
    hits, idx = {}, new_index()
    for q in CFG.ATTACK_QUERIES[n]:
        try:
            got, _, cached = s2.search(q, 10, year_from=CFG.YEAR_FROM)
        except s2.S2Unavailable as e:
            print("[P%d attack] %-65s FAILED (rate limited)" % (n, q[:65]), flush=True)
            log_query(paper=n, query=q, source="semanticscholar", status="failed", stage="attack", detail=str(e)[:100])
            continue
        except s2.S2Persistent as e:
            print("STOP:", e)
            break
        new = sum(add(hits, idx, s2.normalise(p, q, "attack")) for p in got)
        print("[P%d attack] %-65s hits=%d new=%d%s" % (n, q[:65], len(got), new, " (cached)" if cached else ""), flush=True)
        log_query(paper=n, query=q, source="semanticscholar", status="ok", stage="attack", hits=len(got), new_unique=new, cached=cached)
    for r in load_pool(n).values():       # also consider the discovery pool
        add(hits, idx, r)
    save_json(ATTACK / ("paper%d_attack_hits.json" % n), hits)
    outf = ATTACK / ("paper%d_attack.jsonl" % n)
    done = {json.loads(l)["contribution_id"] for l in outf.read_text(encoding="utf-8").splitlines()} if outf.exists() else set()
    for cid, claim in CFG.CONTRIBUTIONS[n]:
        if cid in done:
            continue
        ct = tok(claim)
        cand = sorted((r for r in hits.values() if r.get("abstract")), key=lambda r: -len(ct & tok(r["title"] + " " + r["abstract"])) / (1 + len(ct)))[:8]
        listing = "\n".join("[%d] %s (%s). Abstract: %s" % (i, r["title"], r["year"], r["abstract"][:900]) for i, r in enumerate(cand, 1))
        try:
            res = G.ask(ATTACK_PROMPT.format(claim=claim, papers=listing), max_output_tokens=4000)
        except (G.QuotaExhausted, G.BillingRequired, G.NoKey, G.FreeTierViolation) as e:
            print("STOP:", type(e).__name__, str(e)[:200])
            return
        except RuntimeError as e:
            print("[P%d attack] %s Gemini error: %s" % (n, cid, C.redact(e)[:160]))
            continue
        j = G.parse_json_loose(res["text"]) or {}
        closest = []
        for c in j.get("closest", []) or []:
            try:
                p = cand[int(c["paper_no"]) - 1]
            except (KeyError, ValueError, IndexError, TypeError):
                continue
            closest.append({"title": p["title"], "year": p["year"], "doi": p["doi"], "s2_id": p["s2_id"], "url": p["url"], "evidence_quote": c.get("evidence_quote", ""),
                            "basis": c.get("basis"), "quote_check": quote_status(c.get("evidence_quote", ""), p["abstract"])})
        cls = j.get("classification", "UNPARSED")
        if cls in ("NARROW", "REFRAME", "REMOVE") and not any(c["quote_check"] == "verified" for c in closest):
            cls = cls + "_UNVERIFIED_no_verified_quote"        # a weakening classification without a verified quote is only a lead
        rec = {"contribution_id": cid, "claim": claim, "ts": C.now_utc(), "model": res["model_version"] or G.MODEL, "grounded": False, "classification": cls,
               "confidence": j.get("confidence"), "rationale": j.get("rationale"), "closest": closest, "status": "PROPOSED_model_assisted_human_review_required",
               "papers_considered": [{"s2_id": r["s2_id"], "title": r["title"]} for r in cand]}
        with outf.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("[P%d attack] %s -> %s" % (n, cid, rec["classification"]), flush=True)


# ---------------------------------------------------------------- matrices, source verification, provenance
def short_auth(a):
    p = [x for x in a.split("; ") if x]
    return ", ".join(p[:3]) + (" et al." if len(p) > 3 else "")


def md_cell(s):
    return str(s if s is not None else "").replace("|", "/").replace("\n", " ")


def field(v, key):
    """Return a model-extracted field only if its quote was locally verified; otherwise a marker (unverified content is never propagated)."""
    it = (v or {}).get("extraction", {}).get(key)
    if not it:
        return "not extracted"
    if it.get("status") == "SUPPORTED_BY_SOURCE":
        return it.get("text", "")
    if it.get("status") == "NOT_DETERMINABLE":
        return "not determinable from supplied text"
    return "UNVERIFIED (quote not confirmed; not propagated)"


def overlap_summary(v):
    rows = []
    for cid, it in ((v or {}).get("overlap") or {}).items():
        rel = str(it.get("relation", "")).upper()
        if it.get("status") == "SUPPORTED_BY_SOURCE" and rel in ("SAME", "PARTIAL", "BACKGROUND"):
            rows.append("%s=%s" % (cid, rel))
    return "; ".join(rows) or "none verified"


def implication(v):
    rel = [str(it.get("relation", "")).upper() for it in ((v or {}).get("overlap") or {}).values() if it.get("status") == "SUPPORTED_BY_SOURCE"]
    if "SAME" in rel:
        return "REMOVE/REFRAME candidate (verified SAME-overlap quote; human review required)"
    if "PARTIAL" in rel:
        return "NARROW candidate (verified PARTIAL-overlap quote; human review required)"
    if "BACKGROUND" in rel:
        return "background only (verified)"
    return "no verified implication"


def cite_key(r):
    a = (r["authors"].split("; ")[0].split()[-1] if r["authors"] else "anon")
    a = re.sub(r"[^A-Za-z]", "", a).lower() or "anon"
    w = next((x for x in re.findall(r"[a-z]{4,}", r["title"].lower()) if x not in ("with", "using", "towards", "toward", "from", "that", "this")), "x")
    return "%s%s%s" % (a, r["year"] or "nd", w)


def full_citation(r):
    return "%s, \"%s,\" %s, %s%s." % (short_auth(r["authors"]) or "n/a", r["title"], r["venue"] or "venue not recorded", r["year"] or "n.d.",
                                       (", doi: %s" % r["doi"]) if r["doi"] else "")


MATRIX_COLS = ["citation_key", "full_citation", "year", "venue", "doi_or_url", "task", "method", "dataset_environment", "baselines", "evaluation_metrics", "main_findings",
               "direct_overlap_with_PrepAIred", "threat_to_novelty", "evidence_supporting_us", "evidence_challenging_us", "relevance_papers", "implication",
               "source_verification_status", "oa_pdf_status", "pdf_sha256", "notes"]


def matrix_row(n, r, v, pdf):
    ov = overlap_summary(v)
    basis = (v or {}).get("evidence_basis", "not verified")
    ans = (v or {}).get("answers", {})
    sup = "; ".join("%s: %s" % (q, a.get("text", "")[:110]) for q, a in ans.items() if a.get("status") == "SUPPORTED_BY_SOURCE" and str(a.get("verdict", "")).upper() in ("YES", "PARTIAL"))
    chal = "; ".join("%s: %s" % (q, a.get("text", "")[:110]) for q, a in ans.items() if a.get("status") == "SUPPORTED_BY_SOURCE" and str(a.get("verdict", "")).upper() == "NO")
    threat = "verified overlap: " + ov if ("SAME" in ov or "PARTIAL" in ov) else "no verified overlap with our claims in supplied text"
    nun = sum(1 for grp in ((v or {}).get("extraction", {}), (v or {}).get("answers", {}), (v or {}).get("overlap", {})) for it in grp.values() if it.get("status") == "UNVERIFIED")
    vstat = "not verified" if not v else "%s; basis=%s; unverified_items_excluded=%d" % (v.get("status"), basis, nun)
    if pdf:
        oa = "open-access PDF downloaded; text_status=%s" % pdf.get("text_status")
    else:
        oa = "OA PDF URL listed, not downloaded" if r.get("oa_pdf_url") else "no OA PDF listed in Semantic Scholar"
    return {"citation_key": cite_key(r), "full_citation": full_citation(r), "year": r["year"], "venue": r["venue"], "doi_or_url": r["doi"] or r["url"],
            "task": field(v, "task"), "method": field(v, "method"), "dataset_environment": field(v, "dataset_environment"), "baselines": field(v, "baselines"),
            "evaluation_metrics": field(v, "metrics"), "main_findings": field(v, "main_findings"), "direct_overlap_with_PrepAIred": ov, "threat_to_novelty": threat,
            "evidence_supporting_us": sup or "none verified", "evidence_challenging_us": chal or "none verified", "relevance_papers": "Paper %d" % n, "implication": implication(v),
            "source_verification_status": vstat, "oa_pdf_status": oa, "pdf_sha256": (pdf or {}).get("sha256", ""),
            "notes": "S2 id %s; Gemini analysis is proposed and quote-checked against supplied text only" % r["s2_id"]}


def cmd_matrices():
    pdfs = pdf_index()
    CORE_DIR.mkdir(parents=True, exist_ok=True)
    for n in (1, 2, 3):
        if not (STATE / ("paper%d_core.json" % n)).exists():
            continue
        ver = verification_index(n)
        rows = []
        lines = ["# Paper %d - core literature matrix (screening, not endorsement)\n" % n,
                 "Generated by `free_pipeline/pipeline.py` from Semantic Scholar metadata. Model-extracted fields (task/method/...) come from Gemini 3.6 Flash (non-grounded) "
                 "reading ONLY the abstract and extracted PDF passages this pipeline supplied; a field appears only if its quote was locally verified in the supplied text, "
                 "otherwise it is marked UNVERIFIED and not propagated. Overlap/implication entries are proposals for human review. The same data is in `PAPER%d_CORE_MATRIX.csv`.\n" % n]
        for i, r in enumerate(core_records(n), 1):
            v = (ver.get(r["s2_id"]) or [None])[-1]
            row = matrix_row(n, r, v, pdfs.get(r["s2_id"]))
            rows.append(row)
            lines.append("## P%d-%02d %s" % (n, i, r["title"]))
            for c in MATRIX_COLS:
                lines.append("- **%s**: %s" % (c, md_cell(row[c])))
            lines.append("")
        (CORE_DIR / ("PAPER%d_CORE_MATRIX.md" % n)).write_text("\n".join(lines), encoding="utf-8")
        with (CORE_DIR / ("PAPER%d_CORE_MATRIX.csv" % n)).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=MATRIX_COLS)
            w.writeheader()
            w.writerows(rows)
        print("wrote core/PAPER%d_CORE_MATRIX.md/.csv (%d papers)" % (n, len(rows)))
    sv = ["# Source verification log (core papers)\n",
          "For every core source: bibliographic identity, why selected, which claims it bears on, evidence basis (abstract vs full-text passages), whether each quote was locally "
          "checked, OA/PDF status and hash, and unresolved uncertainties. `quote_check=verified` means the quote is a verbatim (whitespace/punctuation-normalised) substring of the "
          "text supplied to the model. UNVERIFIED items are listed for transparency and are NOT used in the matrices.\n"]
    for n in (1, 2, 3):
        if not (STATE / ("paper%d_core.json" % n)).exists():
            continue
        cj = json.loads((STATE / ("paper%d_core.json" % n)).read_text(encoding="utf-8"))
        ver = verification_index(n)
        for i, r in enumerate(core_records(n), 1):
            v = (ver.get(r["s2_id"]) or [None])[-1]
            p = pdfs.get(r["s2_id"])
            unc = []
            if not r.get("abstract"):
                unc.append("no abstract in Semantic Scholar")
            if not p:
                unc.append("full text not read (no downloaded OA PDF); verification limited to abstract")
            elif p.get("text_status") != "ok":
                unc.append("PDF text extraction: " + p["text_status"])
            if r.get("duplicate_ids"):
                unc.append("merged duplicate S2 ids: " + ", ".join(r["duplicate_ids"]))
            if not r.get("doi"):
                unc.append("no DOI in metadata")
            sv.append("## P%d-%02d %s" % (n, i, r["title"]))
            sv.append("- Identity: %s | %s | %s | DOI %s | URL %s | S2 %s" % (short_auth(r["authors"]), r["year"], r["venue"] or "venue n/a", r["doi"] or "n/a", r["url"], r["s2_id"]))
            sv.append("- Why selected: %s; found by %d quer%s" % (cj.get("decisions", {}).get(r["s2_id"], "n/a"), len(r["found_by"]), "y" if len(r["found_by"]) == 1 else "ies"))
            sv.append("- Bears on claims: %s" % (overlap_summary(v)))
            sv.append("- Evidence basis: %s | OA PDF: %s | PDF sha256: %s" % ((v or {}).get("evidence_basis", "not verified"), r["oa_pdf_url"] or "none", (p or {}).get("sha256", "not downloaded")))
            sv.append("- Gemini (gemini-3.6-flash, non-grounded): %s" % (("status=%s, supplied_text_sha256=%s" % (v["status"], v.get("supplied_text_sha256", "")[:16])) if v else "not performed"))
            if v:
                for grp in ("extraction", "answers", "overlap"):
                    for k, it in (v.get(grp) or {}).items():
                        if it.get("quote") or it.get("status") == "UNVERIFIED":
                            sv.append("  - [%s] %s -> %s | quote_check=%s | \"%s\"" % (grp, k, it.get("status"), it.get("quote_check"), md_cell(it.get("quote", ""))[:170]))
            sv.append("- Unresolved uncertainties: %s\n" % ("; ".join(unc) or "none recorded"))
    (C.ROOT / "SOURCE_VERIFICATION.md").write_text("\n".join(sv), encoding="utf-8")
    na = ["# Novelty attack - model proposals (NOT the final judgement)\n",
          "Each contribution statement was tested against papers found by adversarial queries plus the discovery pool, using ONLY their abstracts, by Gemini 3.6 Flash "
          "(non-grounded). Classes are PROPOSALS requiring human review; a weakening class without a verified quote is suffixed `_UNVERIFIED_no_verified_quote`. "
          "The reviewed judgement is `NOVELTY_ATTACK.md`.\n"]
    for n in (1, 2, 3):
        f = ATTACK / ("paper%d_attack.jsonl" % n)
        if not f.exists():
            continue
        na.append("## Paper %d\n" % n)
        na.append("| Contribution | Proposed class | Confidence | Rationale | Closest sources (quote check) |\n|---|---|---|---|---|")
        for line in f.read_text(encoding="utf-8").splitlines():
            a = json.loads(line)
            cl = "; ".join("%s (%s) [%s] \"%s\"" % (c["title"][:60], c["year"], c["quote_check"], c["evidence_quote"][:90]) for c in a["closest"])
            na.append("| %s: %s | %s | %s | %s | %s |" % (a["contribution_id"], md_cell(a["claim"]), a["classification"], a["confidence"], md_cell(a["rationale"]), md_cell(cl)))
        na.append("")
    ATTACK.mkdir(parents=True, exist_ok=True)
    (ATTACK / "NOVELTY_ATTACK_MODEL_PROPOSALS.md").write_text("\n".join(na), encoding="utf-8")
    write_provenance()
    print("wrote SOURCE_VERIFICATION.md, attack/NOVELTY_ATTACK_MODEL_PROPOSALS.md, PROVENANCE.md")


def write_provenance():
    ql = [json.loads(l) for l in QUERY_LOG.read_text(encoding="utf-8").splitlines()] if QUERY_LOG.exists() else []
    led = [json.loads(l) for l in C.LEDGER.read_text(encoding="utf-8").splitlines()] if C.LEDGER.exists() else []
    g = [x for x in led if x["service"] == "gemini"]
    s = [x for x in led if x["service"] == "semanticscholar"]
    out = ["# Provenance (free literature pipeline)\n",
           "Generated %s by `pipeline.py matrices`.\n" % C.now_utc(),
           "## Configuration\n- Retrieval source: Semantic Scholar Academic Graph API (unauthenticated: %s)\n- Gemini model: gemini-3.6-flash, NON-GROUNDED, analysis/verification of supplied text only\n"
           "- Google Search grounding: NOT used (disabled in code; requests with tools are refused)\n- Billing: not enabled by this tool; no paid API used; Deep Research: not used\n"
           "- Gemini API key: never written to disk; ledger stores status codes and prompt hashes only\n" % ("yes" if not __import__("os").environ.get("SEMANTIC_SCHOLAR_API_KEY") else "no, key used"),
           "## Call counts (from `state/api_ledger.jsonl`, all dates)\n- Semantic Scholar requests: %d (HTTP 200: %d, HTTP 429: %d, other: %d)\n- Gemini attempts: %d (HTTP 200: %d, other: %d)\n"
           % (len(s), sum(x["status"] == 200 for x in s), sum(x["status"] == 429 for x in s), sum(x["status"] not in (200, 429) for x in s), len(g),
              sum(x["status"] == 200 for x in g), sum(x["status"] != 200 for x in g)),
           "## Discovery log (`state/query_log.jsonl`)\n| UTC time | Paper | Stage | Query | Status | Hits | New unique | Cached |\n|---|---|---|---|---|---|---|---|"]
    for q in ql:
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (q["ts"], q.get("paper"), q.get("stage", "discover"), md_cell(q["query"]), q["status"], q.get("hits", ""), q.get("new_unique", ""), q.get("cached", "")))
    out.append("\n## Per-paper pools, deduplication and screening")
    for n in (1, 2, 3):
        pool = load_pool(n)
        cf = STATE / ("paper%d_core.json" % n)
        if not pool:
            out.append("- Paper %d: no pool retrieved" % n)
            continue
        raw = sum(x.get("hits", 0) for x in ql if x.get("paper") == n and x["status"] == "ok" and x.get("stage", "discover") == "discover")
        cj = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {}
        unret = STATE / ("paper%d_unretrieved.json" % n)
        ur = json.loads(unret.read_text(encoding="utf-8"))["queries"] if unret.exists() else []
        out.append("- Paper %d: raw hits across successful queries/expansions %d -> %d unique after DOI / S2-id / normalised-title deduplication; screened top %d as candidates; %d core. Unretrieved queries: %d%s"
                   % (n, raw, len(pool), CFG.TARGETS[n]["pool"], len(cj.get("core", [])), len(ur), (" (" + "; ".join(ur) + ")") if ur else ""))
        for i, d in (cj.get("decisions") or {}).items():
            if d.startswith(("excluded", "included")):
                out.append("  - manual screening: %s %s" % (i, d))
    pdf = pdf_index()
    out.append("\n## PDFs\n%d open-access PDFs downloaded and hashed (`papers/PDF_INDEX.csv`); unavailable/failed listed in `papers/PDF_UNAVAILABLE.csv`.\n" % len(pdf))
    out.append("## Gemini verification\nEvery verification/attack call supplied only the abstract and locally selected PDF passages; quotes were string-checked locally; unverified items are stored as UNVERIFIED and excluded from matrices. See `verification/` and `attack/`.")
    (C.ROOT / "PROVENANCE.md").write_text("\n".join(out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- smoke test and offline self-test
def cmd_smoke():
    import gemini as G
    report = {"date_utc": C.today_utc(), "model": G.MODEL, "grounding": "disabled", "billing_enabled_by_this_tool": False, "deep_research_used": False}
    try:
        data, _cached = s2._get("/graph/v1/paper/search", {"query": "computerized adaptive testing reinforcement learning", "limit": 3, "fields": s2.FIELDS}, use_cache=False)
        got = data.get("data") or []
        report["semantic_scholar"] = {"ok": True, "results_returned": len(got), "rate_limit_events": dict(s2.RATE_EVENTS)}
    except Exception as e:
        report["semantic_scholar"] = {"ok": False, "error": C.redact(e)[:300], "rate_limit_events": dict(s2.RATE_EVENTS)}
    try:
        res = G.ask('Return JSON {"ok": true}', max_output_tokens=1000)
        report["gemini"] = {"ok": True, "model_version": res["model_version"], "finish_reason": res["finish_reason"], "text_preview": res["text"][:80],
                            "service_tier": res["service_tier"], "usage": res["usage"]}
    except Exception as e:
        report["gemini"] = {"ok": False, "reason": type(e).__name__, "detail": C.redact(e)[:300]}
    save_json(STATE / "smoke_report.json", report)
    print(json.dumps(report, indent=1, ensure_ascii=False))


def cmd_selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print("%-66s %s" % (name, "PASS" if cond else "FAIL"))
    mk = lambda i, t, doi="", q="q1", ab="x", c=0, y=2020: {"s2_id": i, "title": t, "authors": "A; B", "year": y, "venue": "", "doi": doi, "arxiv": "", "url": "", "abstract": ab,
                                                          "citation_count": c, "influential_citations": 0, "oa_pdf_url": "", "is_open_access": False, "tldr": "", "found_by": [q], "found_via": ["search"]}
    pool, idx = {}, new_index()
    add(pool, idx, mk("a1", "Computerized Adaptive Testing: A Survey", "10.1/X"))
    add(pool, idx, mk("a2", "Different title", "https://doi.org/10.1/x", q="q2"))          # same DOI, different id/title
    add(pool, idx, mk("a3", "computerized adaptive testing - a survey!", q="q3"))          # same normalised title
    add(pool, idx, mk("a1", "Computerized Adaptive Testing: A Survey", "10.1/X", q="q4"))    # same S2 id
    check("dedupe by DOI / title / paperId -> 1 record", len(pool) == 1)
    check("found_by merged across duplicates", sorted(next(iter(pool.values()))["found_by"]) == ["q1", "q2", "q3", "q4"])
    check("merged duplicate ids recorded, not silently replaced", set(next(iter(pool.values())).get("duplicate_ids", [])) == {"a2", "a3"})
    hi = mk("b1", "Reinforcement learning for adaptive assessment with Elo baseline", ab="We compare a PPO policy against an Elo heuristic baseline in a simulation with equivalence tests.", c=3)
    lo = mk("b2", "A huge unrelated citation classic", ab="Image classification.", c=200000)
    s_hi, c_hi, _ = score(3, hi)
    s_lo, comps_lo, _ = score(3, lo)
    check("relevant low-citation paper outranks irrelevant 200k-citation paper", s_hi > s_lo)
    check("citation bonus is capped (<=1.5)", comps_lo["citations"] <= 1.5)
    sc = screening_scores(hi, c_hi)
    check("screening scores are six 0-3 integers, no overall score", len(sc) == 6 and all(isinstance(x, int) and 0 <= x <= 3 for x in sc.values()))
    src = "Cross-encoders re-score candidates.\nThe model over-\nscored verbose answers."
    check("quote check verbatim (incl. hyphenated line break)", quote_status("The model overscored verbose answers", src) == "verified")
    check("quote check rejects fabricated quote", quote_status("The model beat every human grader by a large margin", src) == "UNVERIFIED_not_in_supplied_text")
    fake = check_item({"verdict": "YES", "basis": "SUPPORTED_BY_SOURCE", "quote": "the model beat every human grader easily", "text": "x"}, src)
    real = check_item({"verdict": "YES", "basis": "SUPPORTED_BY_SOURCE", "quote": "Cross-encoders re-score candidates", "text": "x"}, src)
    check("unsupported Gemini claim -> UNVERIFIED, supported -> SUPPORTED", fake["status"] == "UNVERIFIED" and real["status"] == "SUPPORTED_BY_SOURCE")
    check("redact removes key-shaped strings", "AIza" not in C.redact("x AIzaSyA1234567890abcdefghijklmnopqrstu y"))
    import gemini as G
    check("model is gemini-3.6-flash only; no deep-research/interactions endpoint", G.MODEL == "gemini-3.6-flash" and "deep" not in G.ENDPOINT and "interactions" not in G.ENDPOINT)
    check("grounding disabled: request body has no tools", "tools" not in G.build_body("x") and G.GROUNDING_ENABLED is False)
    try:
        G._guard({"contents": [], "tools": [{"google_search": {}}]})
        tripped = False
    except G.FreeTierViolation:
        tripped = True
    check("guard refuses any request body containing tools", tripped)
    check("hard local call caps configured", G.TOTAL_DAILY_CAP <= 150 and G.RUN_CAP["max"] <= 120)
    check("json loose parser", G.parse_json_loose('text {"a": 1} tail') == {"a": 1})
    check("S2 circuit breaker and jitter present", s2.BREAKER_LIMIT >= 1 and s2.MAX_ATTEMPTS <= 4)
    ps = pick_passages("alpha " * 500 + "cross encoder verbosity bias " * 30 + "omega " * 500, ["verbosity"], k=1)
    check("passage picker returns the relevant window", bool(ps) and "verbosity" in ps[0][1])
    print("SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["smoke", "selftest", "discover", "rank", "verify", "pdfs", "attack", "matrices"])
    ap.add_argument("--paper", type=int, choices=[1, 2, 3], help="default: all three")
    ap.add_argument("--ground", action="store_true", help="REMOVED: Google Search grounding is disabled (free-only workflow)")
    ap.add_argument("--no-expand", action="store_true")
    a = ap.parse_args()
    if a.ground:
        print("Grounding is disabled in this pipeline (free-only). Refusing.")
        return 2
    papers = [a.paper] if a.paper else [1, 2, 3]
    if a.cmd == "smoke":
        return cmd_smoke()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "matrices":
        return cmd_matrices()
    for n in papers:
        {"discover": lambda: cmd_discover(n, not a.no_expand), "rank": lambda: cmd_rank(n), "verify": lambda: cmd_verify(n),
         "pdfs": lambda: cmd_pdfs(n), "attack": lambda: cmd_attack(n)}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main() or 0)
