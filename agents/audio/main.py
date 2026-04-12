"""
PrepAIred Audio Agent — full pipeline
  1. Record (dynamic duration)
  2. Prosodic + STT in parallel
  3. Linguistic analysis
  4. Confidence score
  5. Hesitation score          <- NEW
  6. RL state vector S         <- NEW
  7. Output
"""
import concurrent.futures
import argparse

try:
    from .audio_features    import extract_prosodic_features
    from .confidence_scorer import score
    from .hesitation_scorer import score_hesitation
    from .nlp_analyzer      import analyze_linguistic_confidence
    from .output_formatter  import format_output
    from .recorder          import record_audio
    from .rl_state_vector   import build_state_vector, reset_session
    from .transcriber       import transcribe_and_align
except ImportError:
    from audio_features    import extract_prosodic_features
    from confidence_scorer import score
    from hesitation_scorer import score_hesitation
    from nlp_analyzer      import analyze_linguistic_confidence
    from output_formatter  import format_output
    from recorder          import record_audio
    from rl_state_vector   import build_state_vector, reset_session
    from transcriber       import transcribe_and_align


def run_pipeline(
    duration: int = 10,
    session_id: str = "default",
    difficulty: float = 0.5,
    question_index: int = 0,
    max_questions: int = 10,
) -> dict:
    print("\nPrepAIred Audio Agent")
    print("-" * 40)

    audio_path = record_audio(duration=duration, filename="processed_audio.wav")

    print("Analyzing...")
    with concurrent.futures.ThreadPoolExecutor() as ex:
        p_future = ex.submit(extract_prosodic_features, audio_path)
        t_future = ex.submit(transcribe_and_align, audio_path)
        prosodic      = p_future.result()
        transcription = t_future.result()

    linguistic       = analyze_linguistic_confidence(transcription.get("transcript", ""))
    confidence_score = score(prosodic, transcription, linguistic)
    hesitation       = score_hesitation(prosodic, transcription)
    rl_state         = build_state_vector(
        confidence_score   = confidence_score,
        hesitation         = hesitation,
        transcription      = transcription,
        linguistic         = linguistic,
        session_id         = session_id,
        current_difficulty = difficulty,
        question_index     = question_index,
        max_questions      = max_questions,
    )

    format_output(confidence_score, prosodic, transcription, linguistic)
    _print_rl(hesitation, rl_state)

    return {
        "confidence":    confidence_score,
        "hesitation":    hesitation,
        "rl_state":      rl_state,
        "prosodic":      prosodic,
        "transcription": transcription,
        "linguistic":    linguistic,
    }


def _print_rl(hesitation: dict, rl: dict):
    s = rl["state_vector"]
    print("\nHesitation Breakdown")
    print(f"  Score          : {hesitation['hesitation_score']:.4f}")
    print(f"  Pause ratio    : {hesitation['pause_ratio']:.4f}")
    print(f"  Pause freq/10s : {hesitation['pause_frequency']:.2f}")
    print(f"  Long pauses    : {hesitation['long_pause_count']}")
    print(f"  Filler density : {hesitation['filler_density']:.4f}")
    print(f"  Pitch instab.  : {hesitation['pitch_instability']:.4f}")

    print("\nRL State Vector  S = [Perf, Conf, Hes, Time, Diff]")
    print(f"  S = {s}")
    print(f"  Recommended action -> {rl['recommended_action'].upper()}")
    print("-" * 40 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration",   type=int,   default=10)
    parser.add_argument("--session",    type=str,   default="default")
    parser.add_argument("--difficulty", type=float, default=0.5)
    parser.add_argument("--q-index",    type=int,   default=0)
    parser.add_argument("--max-q",      type=int,   default=10)
    parser.add_argument("--reset",      action="store_true")
    args = parser.parse_args()

    if args.reset:
        reset_session(args.session)

    run_pipeline(
        duration       = args.duration,
        session_id     = args.session,
        difficulty     = args.difficulty,
        question_index = args.q_index,
        max_questions  = args.max_q,
    )
