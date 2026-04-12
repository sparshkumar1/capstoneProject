try:
    from .confidence_scorer import score_breakdown
except ImportError:
    from confidence_scorer import score_breakdown


def format_output(final_score, prosodic, transcription, linguistic):
    breakdown = score_breakdown(prosodic, transcription, linguistic)

    if final_score >= 0.70:
        label = "High Confidence"
    elif final_score >= 0.45:
        label = "Medium Confidence"
    else:
        label = "Low Confidence"

    bar_len = int(final_score * 40)
    bar = "█" * bar_len + "░" * (40 - bar_len)

    print("\n" + "=" * 72)
    print("                     SPEECH CONFIDENCE ASSESSMENT")
    print("=" * 72)
    print(f"\nTranscript:\n  {transcription.get('transcript', '')}\n")
    print(f"Confidence: [{bar}] {final_score:.4f}  ({label})")

    print("\nLayer 1 - Prosodic / Voice Quality")
    print(f"  Jitter        : {prosodic.get('jitter', 0):.6f}")
    print(f"  Shimmer       : {prosodic.get('shimmer', 0):.6f}")
    print(f"  HNR           : {prosodic.get('hnr', 0):.4f}")
    print(f"  Pitch mean    : {prosodic.get('pitch_mean', 0):.2f}")
    print(f"  Pitch stddev  : {prosodic.get('pitch_stddev', 0):.2f}")
    print(f"  Signal RMS    : {prosodic.get('signal_rms', 0):.6f}")
    print(f"  Voice source  : {prosodic.get('voice_quality_source', 'n/a')}")
    print(f"  Voice quality : {breakdown['voice_quality']:.4f}")

    print("\nLayer 2 - Transcription / Fluency")
    print(f"  Pause count    : {transcription.get('pause_count', 0)}")
    print(f"  Total pauses   : {transcription.get('total_pause_time', 0):.3f}s")
    print(f"  Speech time    : {transcription.get('total_speech_time', 0):.3f}s")
    print(f"  Audio duration : {transcription.get('audio_duration', 0):.3f}s")
    print(f"  Speaking rate  : {transcription.get('true_speaking_rate', 0):.2f} words/sec")
    print(f"  Fluency score  : {breakdown['fluency_score']:.4f}")
    print(f"  Rhythm score   : {breakdown.get('rhythm_score', 0):.4f}")
    print(f"  Pause ratio    : {breakdown.get('pause_ratio', 0):.4f}")
    print(f"  ASR confidence : {breakdown.get('asr_confidence', 0):.4f}")
    print(f"  Align source   : {transcription.get('alignment_source', 'unknown')}")

    print("\nLayer 3 - Linguistic Confidence")
    print(f"  Label          : {linguistic.get('label', 'neutral')}")
    print(f"  Score          : {linguistic.get('linguistic_score', 0):.4f}")
    print(f"  Label scores   : {linguistic.get('label_scores', {})}")
    print(f"  Source         : {linguistic.get('analysis_source', 'unknown')}")

    print("\nFinal Blend")
    print(f"  Voice quality  : {breakdown['voice_quality']:.4f}  (28%)")
    print(f"  Linguistic     : {breakdown['ling_score']:.4f}  (27%)")
    print(f"  Fluency        : {breakdown['fluency_score']:.4f}  (22%)")
    print(f"  Rate score     : {breakdown['rate_score']:.4f}  (13%)")
    print(f"  Rhythm score   : {breakdown.get('rhythm_score', 0):.4f}  (10%)")
    print("=" * 72 + "\n")