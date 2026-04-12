import { useMemo } from "react";

export default function WaveformBar({ level = 0, isActive = false, barCount = 20 }) {
  const timing = useMemo(
    () => Array.from({ length: barCount }, (_, i) => ({
      duration: 0.62 + (i % 5) * 0.07,
      delay: i * 0.04,
    })),
    [barCount]
  );

  const bars = Array.from({ length: barCount }, (_, i) => {
    // Each bar has a phase so they animate differently
    const phase = (i / barCount) * Math.PI * 2;
    const naturalFreq = 0.3 + Math.sin(phase) * 0.2;
    const driven = isActive ? level * (0.45 + Math.abs(Math.sin(phase)) * 0.55) : 0;
    return Math.max(0.08, naturalFreq * 0.1 + driven);
  });

  return (
    <div style={{
      display: "flex", alignItems: "center",
      gap: 3, height: 40, paddingTop: 4
    }}>
      {bars.map((h, i) => (
        <div key={i} style={{
          flex: 1,
          height: `${h * 100}%`,
          minHeight: 3,
          borderRadius: 99,
          background: isActive
            ? `linear-gradient(to top, var(--accent), var(--accent-2))`
            : "var(--border-hi)",
          animationName: isActive ? "waveform" : "none",
          animationDuration: `${timing[i]?.duration ?? 0.7}s`,
          animationTimingFunction: "ease-in-out",
          animationIterationCount: "infinite",
          animationDirection: "alternate",
          animationDelay: isActive ? `${timing[i]?.delay ?? 0}s` : undefined,
          transition: "height 0.1s ease",
        }} />
      ))}
    </div>
  );
}
