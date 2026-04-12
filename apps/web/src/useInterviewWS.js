import { useEffect, useRef, useCallback } from "react";

function resolveWsBase() {
  const envWs = import.meta.env.VITE_WS_URL;
  if (envWs) return envWs.replace(/\/$/, "");

  const envApi = import.meta.env.VITE_API_URL;
  if (envApi) return envApi.replace(/^http/i, "ws").replace(/\/$/, "");

  if (typeof window !== "undefined") {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.hostname === "localhost" ? "127.0.0.1" : window.location.hostname;
    return `${protocol}://${host}:8000`;
  }

  return "ws://127.0.0.1:8000";
}

const WS_BASE = resolveWsBase();

export function useInterviewWS(sessionId, handlers = {}) {
  const ws = useRef(null);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;

  const send = useCallback((type, payload = {}) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  useEffect(() => {
    if (!sessionId || sessionId === "demo-session") return;

    const socket = new WebSocket(`${WS_BASE}/ws/interview/${sessionId}`);
    ws.current = socket;

    socket.onopen = () => {
      console.log("[WS] Connected:", sessionId);
      handlersRef.current.onOpen?.();
    };

    socket.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        const h = handlersRef.current;
        switch (msg.type) {
          case "question":        h.onQuestion?.(msg.payload);     break;
          case "feedback":        h.onFeedback?.(msg.payload);     break;
          case "difficulty_update": h.onDifficulty?.(msg.payload); break;
          case "hint":            h.onHint?.(msg.payload);         break;
          case "session_end":     h.onEnd?.(msg.payload);          break;
          case "code_result":     h.onCodeResult?.(msg.payload);   break;
          case "error":           h.onError?.(msg.payload);        break;
          default:                h.onRaw?.(msg);
        }
      } catch (err) {
        console.error("[WS] Parse error:", err);
      }
    };

    socket.onerror = (e) => {
      console.error("[WS] Error:", e);
      handlersRef.current.onError?.({ message: "WebSocket error" });
    };

    socket.onclose = () => {
      console.log("[WS] Disconnected");
      handlersRef.current.onClose?.();
    };

    return () => socket.close();
  }, [sessionId]);

  return { send };
}
