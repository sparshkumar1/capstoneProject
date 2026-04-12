export default function ScoreRing({ score = 0, size = 96, label = "", color = "var(--accent)" }) {
  const r = (size / 2) - 8;
  const circ = 2 * Math.PI * r;
  const fill = circ * (1 - score / 100);

  return (
    <div className="score-ring-wrap">
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke="var(--surface-2)" strokeWidth={7} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth={7}
          strokeDasharray={circ}
          strokeDashoffset={fill}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(.4,0,.2,1)" }}
        />
      </svg>
      <div style={{ marginTop: -size / 2 - 4, textAlign: "center" }}>
        <div style={{ fontFamily: "Syne", fontWeight: 800, fontSize: size * 0.22, color }}>
          {Math.round(score)}
        </div>
        {label && <div style={{ fontSize: 11, color: "var(--text-3)", marginTop: 2 }}>{label}</div>}
      </div>
    </div>
  );
}
