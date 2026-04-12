import { useState, useRef, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function useVoiceRecorder({ onTranscript, sessionId }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [durationMs, setDurationMs] = useState(0);
  const [micError, setMicError] = useState("");

  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const analyser = useRef(null);
  const animFrame = useRef(null);
  const startTime = useRef(null);
  const durationTimer = useRef(null);
  const stream = useRef(null);
  const recognition = useRef(null);
  const browserTranscript = useRef("");

  const measureLevel = useCallback(() => {
    if (!analyser.current) return;
    const data = new Uint8Array(analyser.current.frequencyBinCount);
    analyser.current.getByteTimeDomainData(data);
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      const v = (data[i] - 128) / 128;
      sum += v * v;
    }
    const rms = Math.sqrt(sum / data.length);
    setAudioLevel(Math.min(1, rms * 6));
    animFrame.current = requestAnimationFrame(measureLevel);
  }, []);

  const startRecording = useCallback(async () => {
    try {
      setIsPreparing(true);
      setMicError("");
      browserTranscript.current = "";

      if (!window.isSecureContext) {
        throw new Error("Microphone requires a secure context. Use localhost or HTTPS.");
      }

      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("This browser context does not support microphone capture. Try Chrome or Edge.");
      }

      const s = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.current = s;

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const rec = new SpeechRecognition();
        rec.lang = "en-US";
        rec.interimResults = true;
        rec.continuous = true;
        rec.onresult = (event) => {
          browserTranscript.current = Array.from(event.results)
            .map((result) => result[0]?.transcript || "")
            .join(" ")
            .replace(/\s+/g, " ")
            .trim();
        };
        rec.onerror = (event) => {
          console.warn("[Voice] Speech recognition error:", event.error);
        };
        recognition.current = rec;
        rec.start();
      }

      // Audio analysis
      const ctx = new AudioContext();
      const src = ctx.createMediaStreamSource(s);
      const an = ctx.createAnalyser();
      an.fftSize = 256;
      src.connect(an);
      analyser.current = an;

      const mr = new MediaRecorder(s, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });

      audioChunks.current = [];
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      mr.onstop = async () => {
        cancelAnimationFrame(animFrame.current);
        clearInterval(durationTimer.current);
        setAudioLevel(0);

        const blob = new Blob(audioChunks.current, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", blob, "recording.webm");
        formData.append("session_id", sessionId || "");
        if (browserTranscript.current.trim()) {
          formData.append("transcript", browserTranscript.current.trim());
        }

        try {
          const res = await fetch(`${API_BASE}/api/transcribe`, {
            method: "POST",
            body: formData,
          });
          if (res.ok) {
            const data = await res.json();
            const transcriptText = (data.transcript || browserTranscript.current || "").trim();
            onTranscript?.(transcriptText, blob, data.audio_analysis || null);
          }
        } catch (err) {
          console.error("[Voice] Transcription error:", err);
          onTranscript?.((browserTranscript.current || "[transcription failed]").trim(), blob);
        }
      };

      mr.start(250);
      mediaRecorder.current = mr;
      startTime.current = Date.now();
      setDurationMs(0);

      durationTimer.current = setInterval(() => {
        setDurationMs(Date.now() - startTime.current);
      }, 100);

      setIsPreparing(false);
      setIsRecording(true);
      measureLevel();
    } catch (err) {
      setIsPreparing(false);
      const name = err?.name || "Error";
      if (name === "NotAllowedError") {
        setMicError("Microphone permission was denied. Allow mic access for this site and try again.");
      } else if (name === "NotFoundError") {
        setMicError("No microphone device was found. Connect a mic and retry.");
      } else if (name === "NotReadableError") {
        setMicError("Microphone is busy in another app. Close other apps using the mic and retry.");
      } else {
        setMicError(err?.message || "Unable to access microphone.");
      }
      console.error("[Voice] Mic access denied:", err);
    }
  }, [sessionId, onTranscript, measureLevel]);

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current?.state === "recording") {
      mediaRecorder.current.stop();
      stream.current?.getTracks().forEach(t => t.stop());
      if (recognition.current) {
        recognition.current.stop();
        recognition.current = null;
      }
      setIsRecording(false);
    }
  }, []);

  const formatDuration = (ms) => {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    return `${m}:${String(s % 60).padStart(2, "0")}`;
  };

  return {
    isRecording, isPreparing, audioLevel,
    micError,
    durationMs, durationLabel: formatDuration(durationMs),
    startRecording, stopRecording,
  };
}
