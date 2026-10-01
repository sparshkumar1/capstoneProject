"""
Deterministic speaking-rate sweep for the confidence/hesitation scorers.

No randomness, no new data collection, no model calls. Calls the real,
unmodified `agents.audio.confidence_scorer.score_breakdown` and
`agents.audio.hesitation_scorer.score_hesitation` across a realistic range
of WPM inputs (what `agents/audio/transcriber.py` actually produces) and a
realistic range of WPS inputs (what the two scorer functions assume), with
all other fields held fixed at representative values.

Run before and after the WPM->WPS unit fix, output written to a
run-labeled JSON file (before/after), never overwritten in place.

Usage: python speaking_rate_sweep.py <label>
  <label> is "before" or "after" (or any string); output goes to
  ../results/speaking_rate_sweep/sweep_<label>.json
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from agents.audio.confidence_scorer import score_breakdown  # noqa: E402
from agents.audio.hesitation_scorer import score_hesitation  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "results" / "speaking_rate_sweep"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIXED_PROSODIC = {"jitter": 0.015, "shimmer": 0.05, "hnr": 20.0, "pitch_stddev": 35.0}
FIXED_LINGUISTIC = {"linguistic_score": 0.6}

WPM_SWEEP = [40.0, 60.0, 80.0, 100.0, 120.0, 126.0, 140.0, 160.0, 180.0, 200.0, 220.0, 258.0, 280.0, 320.0]
WPS_SWEEP = [0.5, 1.0, 1.5, 2.0, 2.1, 2.5, 3.0, 3.2, 3.5, 4.0, 4.3, 4.5, 5.0, 6.0]
INVALID_INPUTS = [0.0, -10.0, None, "not_a_number", float("nan")]


def make_transcription(rate_value):
    d = {
        "total_speech_time": 4.0,
        "total_pause_time": 0.4,
        "transcription_confidence": 0.9,
        "pause_count": 1,
        "words": [],
        "transcript": "",
        "audio_duration": 4.4,
        "pauses": [],
    }
    if rate_value is not None:
        d["true_speaking_rate"] = rate_value
    return d


def run_point(rate_value, rate_label):
    trans = make_transcription(rate_value)
    try:
        conf = score_breakdown(FIXED_PROSODIC, trans, FIXED_LINGUISTIC)
        conf_err = None
    except Exception as e:
        conf = None
        conf_err = f"{type(e).__name__}: {e}"
    try:
        hes = score_hesitation(FIXED_PROSODIC, trans)
        hes_err = None
    except Exception as e:
        hes = None
        hes_err = f"{type(e).__name__}: {e}"
    return {
        "rate_input": rate_label,
        "rate_raw_value": None if rate_value is None else (str(rate_value) if not isinstance(rate_value, (int, float)) else rate_value),
        "confidence_rate_score": None if conf is None else conf["rate_score"],
        "confidence_final_score": None if conf is None else conf["final_score"],
        "confidence_error": conf_err,
        "hesitation_rate_deviation": None if hes is None else hes["rate_deviation"],
        "hesitation_score": None if hes is None else hes["hesitation_score"],
        "hesitation_error": hes_err,
    }


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "unlabeled"
    results = {
        "label": label,
        "wpm_sweep": [run_point(v, f"{v}_WPM") for v in WPM_SWEEP],
        "wps_sweep_direct_field_value": [run_point(v, f"{v}_direct") for v in WPS_SWEEP],
        "invalid_inputs": [run_point(v, f"invalid_{v!r}") for v in INVALID_INPUTS],
        "missing_field": [run_point(None, "missing_field_default")],
    }
    out_path = OUT_DIR / f"sweep_{label}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Wrote {out_path}")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
