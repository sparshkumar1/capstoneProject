import { useRef, useEffect, useState } from "react";

// Dynamic import of Monaco from CDN (loaded in index.html)
const STARTER_C = `#include <stdio.h>

int main() {
    // Write your solution here
    
    return 0;
}
`;

export default function MonacoEditor({ value, onChange, readOnly = false, height = "100%" }) {
  const containerRef = useRef(null);
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const [isMonacoReady, setIsMonacoReady] = useState(Boolean(window.monaco));
  const [useFallback, setUseFallback] = useState(false);

  useEffect(() => {
    let timer = null;
    let interval = null;

    const initEditor = () => {
      if (!window.monaco || !containerRef.current) return;
      monacoRef.current = window.monaco;
      setIsMonacoReady(true);
      setUseFallback(false);

      // Register C language tokens
      try {
        window.monaco.languages.register({ id: "c" });
      } catch {
        // Ignore if already registered
      }

      const editor = window.monaco.editor.create(containerRef.current, {
        value: value ?? STARTER_C,
        language: "c",
        theme: document.documentElement.getAttribute("data-theme") === "light"
          ? "vs" : "prepaired-dark",
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Courier New', monospace",
        fontLigatures: true,
        minimap: { enabled: false },
        lineNumbers: "on",
        scrollBeyondLastLine: false,
        wordWrap: "on",
        readOnly,
        automaticLayout: true,
        padding: { top: 16, bottom: 16 },
        scrollbar: { verticalScrollbarSize: 6, horizontalScrollbarSize: 6 },
        suggestOnTriggerCharacters: true,
        quickSuggestions: true,
        renderLineHighlight: "gutter",
        cursorBlinking: "smooth",
        cursorSmoothCaretAnimation: "on",
        bracketPairColorization: { enabled: true },
        formatOnPaste: true,
      });

      // Define custom dark theme
      window.monaco.editor.defineTheme("prepaired-dark", {
        base: "vs-dark",
        inherit: true,
        rules: [
          { token: "keyword", foreground: "4f7eff", fontStyle: "bold" },
          { token: "type", foreground: "00e5c8" },
          { token: "comment", foreground: "555d78", fontStyle: "italic" },
          { token: "string", foreground: "36d98f" },
          { token: "number", foreground: "ffb84f" },
          { token: "delimiter", foreground: "8890a8" },
        ],
        colors: {
          "editor.background": "#0d0f17",
          "editor.foreground": "#e8eaf2",
          "editor.lineHighlightBackground": "#161922",
          "editorLineNumber.foreground": "#3a4060",
          "editorLineNumber.activeForeground": "#8890a8",
          "editor.selectionBackground": "#4f7eff33",
          "editor.inactiveSelectionBackground": "#4f7eff1a",
          "editorCursor.foreground": "#4f7eff",
          "editorIndentGuide.background": "#1c2030",
          "editorIndentGuide.activeBackground": "#242840",
        },
      });

      window.monaco.editor.setTheme(
        document.documentElement.getAttribute("data-theme") === "light" ? "vs" : "prepaired-dark"
      );

      editor.onDidChangeModelContent(() => {
        onChange?.(editor.getValue());
      });

      editorRef.current = editor;
    };

    // Check if Monaco is already loaded
    if (window.monaco) {
      initEditor();
    } else {
      window.__onMonacoReady = initEditor;
      interval = setInterval(() => {
        if (window.monaco) {
          clearInterval(interval);
          initEditor();
        }
      }, 100);

      // Fallback timeout after 2.5 seconds if CDN is blocked / offline
      timer = setTimeout(() => {
        if (!window.monaco) {
          clearInterval(interval);
          setUseFallback(true);
        }
      }, 2500);
    }

    return () => {
      if (interval) clearInterval(interval);
      if (timer) clearTimeout(timer);
      editorRef.current?.dispose();
    };
  }, []);

  // Sync theme changes
  useEffect(() => {
    const observer = new MutationObserver(() => {
      if (!monacoRef.current) return;
      const t = document.documentElement.getAttribute("data-theme");
      monacoRef.current.editor.setTheme(t === "light" ? "vs" : "prepaired-dark");
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  // Sync external value changes (e.g. question template)
  useEffect(() => {
    if (editorRef.current && value !== undefined) {
      const current = editorRef.current.getValue();
      if (current !== value) {
        editorRef.current.setValue(value);
      }
    }
  }, [value]);

  if (useFallback) {
    return (
      <div className="monaco-fallback-container" style={{ width: "100%", height, display: "flex", flexDirection: "column" }}>
        <div className="fallback-editor-banner" style={{
          fontSize: 11,
          padding: "6px 12px",
          background: "rgba(255, 184, 79, 0.12)",
          borderBottom: "1px solid rgba(255, 184, 79, 0.3)",
          color: "var(--warn)",
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}>
          <span>⚠️</span>
          <span>Advanced editor unavailable. Basic code editor is active.</span>
        </div>
        <textarea
          className="fallback-code-editor"
          value={value ?? STARTER_C}
          onChange={(e) => onChange?.(e.target.value)}
          readOnly={readOnly}
          spellCheck={false}
          style={{
            flex: 1,
            width: "100%",
            height: "100%",
            minHeight: 220,
            background: "var(--surface)",
            color: "var(--text-1)",
            fontFamily: "'JetBrains Mono', 'Courier New', monospace",
            fontSize: 14,
            lineHeight: 1.5,
            padding: 14,
            border: "none",
            outline: "none",
            resize: "none",
            boxSizing: "border-box",
          }}
        />
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ width: "100%", height, minHeight: 200 }} />
  );
}
