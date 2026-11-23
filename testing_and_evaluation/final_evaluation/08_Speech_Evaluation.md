# Speech (WhisperX/faster-whisper) Evaluation — Final Evaluation Phase

## Status, re-confirmed this phase

`pip show whisperx` and `pip show faster-whisper` both report "Package(s) not found" in this `.venv`, confirmed fresh this phase (unchanged from the discovery made earlier in this engagement). Direct `import whisperx` raises `ModuleNotFoundError`. `agents/audio/transcriber.py`'s `_WHISPERX_AVAILABLE` flag is therefore `False`, and every call to `transcribe_and_align()` returns the energy-based fallback (no transcript) immediately, with no exception raised (this is the module's own, intentional "package absent" code path, not an error state). Re-confirmed against the real `tests/test_candidate_hash_table_answer.wav` fixture this phase: identical result to the prior capture (empty transcript, `alignment_source: wav_energy_fallback`, fixed `transcription_confidence: 0.35`).

## Why no WER/CER number is reported here

This phase's instructions are explicit: **"If reference transcripts do not exist, create an evaluation protocol rather than inventing WER or CER results."** No reference-transcript dataset exists anywhere in this repository for `tests/test_candidate_hash_table_answer.wav` or any other audio fixture (confirmed by a targeted search of `tests/` and `data/` for any `.txt`/`.json` sidecar with matching content before this phase; none found). Additionally, the engine that would need to be evaluated (WhisperX) is not installed in this environment, so even a correctly-labeled fixture could not be run through the real engine here. **No WER, CER, or accuracy number is reported in this document or anywhere else this phase**, consistent with the instruction.

## Evaluation protocol (defined, not executed)

For future execution, once WhisperX is installed and reference transcripts exist:

1. **Dataset:** record (or source, with consent) at least 10–20 short (10–30s) spoken technical answers, each independently, manually transcribed by a human to produce a verified ground-truth reference transcript. Cover a range of speaking rates, accents, and background-noise conditions representative of real candidates, disclosed explicitly in the resulting report.
2. **Metric computation:** for each sample, run the real `transcribe_and_align()` function (not the HTTP wrapper, to isolate STT-specific latency from request overhead) and compute Word Error Rate and Character Error Rate against the human reference using a standard, cited library (e.g. `jiwer`), not a hand-rolled edit-distance implementation.
3. **Reporting:** report per-sample and aggregate (mean, median, worst-case) WER/CER, plus the fraction of samples where the fallback path activated (engine unavailable or decode failure) versus genuinely transcribed — these are a different statistic from WER/CER and must not be merged into one number.
4. **Latency:** measure separately, warm vs. cold-start, consistent with `09_Performance_and_Reliability.md`'s methodology.
5. **Failure analysis:** for any sample with WER above a threshold (e.g. 30%), manually inspect whether the error is attributable to the model, the audio quality, or a genuine out-of-vocabulary technical term (expected to be a real source of error for CS terminology).

## What this phase did instead (real, executed evidence)

- Confirmed, via direct dependency inspection, **why** no real STT evidence can currently be gathered in this environment (a root-cause finding, not previously established this precisely — see `Application_Code_Changes.md`'s related discussion and the earlier comprehensive testing report's DEF-002).
- Confirmed the **fallback path itself** is robust: it does not crash, returns a well-formed structured response, and uses a fixed, clearly-labeled placeholder confidence value (`0.35`) rather than a fabricated one. This is genuine, positive, executed evidence about the *fallback's* reliability — explicitly not evidence about transcription accuracy, which remains entirely unestablished.
