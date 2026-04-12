export default function DifficultyTracker({ current = 3, history = [], max = 5 }) {
  const labels = ["Easy", "Medium-Low", "Medium", "Medium-Hard", "Hard"];
  const colors = ["var(--success)", "#7bcf6b", "var(--warn)", "#ff8c4f", "var(--danger)"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em", fontFamily: "Syne", fontWeight: 600 }}>
          Difficulty
        </span>
        <span style={{ fontSize: 12, color: colors[current - 1], fontWeight: 700, fontFamily: "Syne" }}>
          {labels[current - 1] || "—"}
        </span>
      </div>

      {/* Level dots */}
      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
        {Array.from({ length: max }, (_, i) => (
          <div key={i} style={{
            flex: 1, height: 6,
            borderRadius: 99,
            background: i < current ? colors[i] : "var(--surface-2)",
            transition: "background 0.4s ease",
            boxShadow: i === current - 1 ? `0 0 8px ${colors[i]}` : "none",
          }} />
        ))}
      </div>

      {/* History sparkline */}
      {history.length > 1 && (
        <svg width="100%" height={24} style={{ marginTop: 4 }}>
          {history.map((v, i) => {
            const x = (i / (history.length - 1)) * 100;
            const y = 100 - (v / max) * 100;
            const nextX = history[i + 1] !== undefined ? ((i + 1) / (history.length - 1)) * 100 : null;
            const nextY = history[i + 1] !== undefined ? 100 - (history[i + 1] / max) * 100 : null;
            return (
              <g key={i}>
                {nextX !== null && (
                  <line
                    x1={`${x}%`} y1={`${y}%`}
                    x2={`${nextX}%`} y2={`${nextY}%`}
                    stroke="var(--accent)" strokeWidth={1.5} strokeOpacity={0.5}
                  />
                )}
                <circle cx={`${x}%`} cy={`${y}%`} r={2.5}
                  fill={colors[v - 1] || "var(--accent)"} />
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}
