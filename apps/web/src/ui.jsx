/**
 * ui.jsx — small shared UI kit for the PrepAIred app shell and insight pages.
 * Icons are inline SVG (no emoji, no icon dependency); charts are plain SVG so no chart library is needed.
 */
import { useCallback, useEffect, useRef, useState } from "react";

const ICONS = {
  home: <><path d="M3 11.5 12 3l9 8.5" /><path d="M5 10v10h5v-6h4v6h5V10" /></>,
  play: <path d="M6 4l14 8-14 8V4z" />,
  target: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1" /></>,
  chart: <><path d="M4 20V10" /><path d="M10 20V4" /><path d="M16 20v-7" /><path d="M22 20H2" /></>,
  cards: <><path d="M12 2 2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" /></>,
  book: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15z" /></>,
  user: <><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></>,
  logout: <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><path d="m16 17 5-5-5-5" /><path d="M21 12H9" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  mic: <><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><path d="M12 19v3" /></>,
  code: <><path d="m16 18 6-6-6-6" /><path d="m8 6-6 6 6 6" /></>,
  flame: <path d="M12 2c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-5 1-9z" />,
  check: <path d="M20 6 9 17l-5-5" />,
  alert: <><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" /><path d="M12 9v4" /><path d="M12 17h.01" /></>,
  arrow: <><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></>,
  refresh: <><path d="M21 4v6h-6" /><path d="M3 20v-6h6" /><path d="M3.5 9a9 9 0 0 1 14.9-3.4L21 10" /><path d="M3 14l2.6 4.4A9 9 0 0 0 20.5 15" /></>,
  compare: <><circle cx="18" cy="18" r="3" /><circle cx="6" cy="6" r="3" /><path d="M13 6h3a2 2 0 0 1 2 2v7" /><path d="M6 9v12" /></>,
  calendar: <><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4" /><path d="M8 2v4" /><path d="M3 10h18" /></>,
  sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>,
  moon: <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />,
  up: <><path d="m23 6-9.5 9.5-5-5L1 18" /><path d="M17 6h6v6" /></>,
  down: <><path d="m23 18-9.5-9.5-5 5L1 6" /><path d="M17 18h6v-6" /></>,
  x: <path d="M18 6 6 18M6 6l12 12" />,
  stop: <rect x="6" y="6" width="12" height="12" rx="1.5" />,
  info: <><circle cx="12" cy="12" r="9" /><path d="M12 16v-4" /><path d="M12 8h.01" /></>,
  skip: <><path d="M5 4l10 8-10 8V4z" /><path d="M19 5v14" /></>,
  bulb: <><path d="M9 18h6" /><path d="M10 22h4" /><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2V17h6v-.3c0-.8.4-1.5 1-2A7 7 0 0 0 12 2z" /></>,
  list: <><path d="M8 6h13M8 12h13M8 18h13" /><path d="M3 6h.01M3 12h.01M3 18h.01" /></>,
  flip: <><path d="M3 12a9 9 0 0 1 15-6.7L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-15 6.7L3 16" /><path d="M3 21v-5h5" /></>,
};

export function Icon({ name, size = 18, className = "", title }) {
  const body = ICONS[name];
  if (!body) return null;
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={title ? undefined : true}
      role={title ? "img" : undefined}
    >
      {title && <title>{title}</title>}
      {body}
    </svg>
  );
}

/* ── formatting helpers ─────────────────────────────────────────────── */
export const pct = (v, digits = 0) => (v === null || v === undefined || Number.isNaN(v) ? "—" : `${(v * 100).toFixed(digits)}%`);

export function formatDate(iso, opts = { month: "short", day: "numeric" }) {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString(undefined, opts);
}

export function formatDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

export const BAND_META = {
  strong: { label: "Strong", tone: "success" },
  developing: { label: "Developing", tone: "warn" },
  needs_work: { label: "Needs work", tone: "danger" },
  unknown: { label: "No data", tone: "neutral" },
};

export function tzOffsetMinutes() {
  return -new Date().getTimezoneOffset();
}

/* ── data loading hook ──────────────────────────────────────────────── */
export function useAsync(loader, deps) {
  const [state, setState] = useState({ loading: true, data: null, error: null });
  const loaderRef = useRef(loader);
  loaderRef.current = loader;
  const run = useCallback(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.resolve()
      .then(() => loaderRef.current())
      .then((data) => { if (!cancelled) setState({ loading: false, data, error: null }); })
      .catch((error) => { if (!cancelled) setState({ loading: false, data: null, error }); });
    return () => { cancelled = true; };
  }, []);
  useEffect(() => run(), deps);
  return { ...state, reload: run };
}

/* ── small presentational components ────────────────────────────────── */
export function Badge({ tone = "neutral", children, title }) {
  return <span className={`pill pill-${tone}`} title={title}>{children}</span>;
}

export function Skeleton({ height = 16, width = "100%", style }) {
  return <span className="sk" style={{ height, width, ...style }} aria-hidden="true" />;
}

export function EmptyState({ icon = "info", title, children, action }) {
  return (
    <div className="empty">
      <span className="empty-icon"><Icon name={icon} size={22} /></span>
      <h4>{title}</h4>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ error, onRetry, what = "this data" }) {
  const message = (error && error.message) || "Request failed";
  const offline = /failed to fetch|network/i.test(message);
  return (
    <div className="empty empty-error" role="alert">
      <span className="empty-icon"><Icon name="alert" size={22} /></span>
      <h4>Could not load {what}</h4>
      <p>{offline ? "The backend is not reachable on port 8000. Start it and try again." : message}</p>
      {onRetry && <button type="button" className="btn btn-ghost btn-sm" onClick={onRetry}><Icon name="refresh" size={14} /> Retry</button>}
    </div>
  );
}

export function Meter({ value, tone, label, height = 8, className = "" }) {
  const w = Math.max(0, Math.min(1, value ?? 0)) * 100;
  return (
    <div className={`meter ${className}`} style={{ height }} role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(w)} aria-label={label}>
      <span className={`meter-fill tone-${tone || "accent"}`} style={{ width: `${w}%` }} />
    </div>
  );
}

/* ── charts ─────────────────────────────────────────────────────────── */
/**
 * LineChart — points: [{ label, value (0..1), detail? }]. Draws the evaluator band boundaries (0.40 / 0.60).
 */
export function LineChart({ points, height = 200, ariaLabel = "Score trend", bands = true }) {
  const W = 640, H = height, padL = 38, padR = 14, padT = 12, padB = 26;
  const n = points.length;
  if (!n) return null;
  const x = (i) => padL + (n === 1 ? (W - padL - padR) / 2 : (i * (W - padL - padR)) / (n - 1));
  const y = (v) => padT + (1 - Math.max(0, Math.min(1, v))) * (H - padT - padB);
  const path = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const area = `${path} L${x(n - 1).toFixed(1)},${y(0)} L${x(0).toFixed(1)},${y(0)} Z`;
  const ticks = [0, 0.25, 0.5, 0.75, 1];
  const labelEvery = Math.max(1, Math.ceil(n / 7));
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={ariaLabel} preserveAspectRatio="none">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={padL} x2={W - padR} y1={y(t)} y2={y(t)} className="gl" />
          <text x={padL - 8} y={y(t) + 4} className="axis" textAnchor="end">{Math.round(t * 100)}</text>
        </g>
      ))}
      {bands && [0.4, 0.6].map((t) => (
        <line key={t} x1={padL} x2={W - padR} y1={y(t)} y2={y(t)} className="band" />
      ))}
      {n > 1 && <path d={area} className="area" />}
      {n > 1 && <path d={path} className="line" />}
      {points.map((p, i) => (
        <g key={i}>
          <circle cx={x(i)} cy={y(p.value)} r={n > 30 ? 2.6 : 4} className="dot">
            <title>{`${p.label}: ${Math.round(p.value * 100)}%${p.detail ? ` — ${p.detail}` : ""}`}</title>
          </circle>
          {i % labelEvery === 0 && (
            <text x={x(i)} y={H - 8} className="axis" textAnchor="middle">{p.label}</text>
          )}
        </g>
      ))}
    </svg>
  );
}

/** Dots showing the last few outcomes of a concept: c = covered, m = missing. */
export function OutcomeDots({ recent }) {
  if (!recent?.length) return null;
  return (
    <span className="dots" aria-label={`Recent outcomes: ${recent.map((r) => (r === "c" ? "covered" : "missed")).join(", ")}`}>
      {recent.map((r, i) => <span key={i} className={`dot-${r}`} />)}
    </span>
  );
}
