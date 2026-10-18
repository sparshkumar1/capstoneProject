import { useContext, useMemo, useState } from "react";
import { SessionContext } from "./contexts";
import Shell from "./Shell";
import { api } from "./api";
import { startPractice, repeatLastSetup } from "./practice";
import {
  BAND_META, Badge, EmptyState, ErrorState, Icon, LineChart, Meter, Skeleton,
  formatDate, pct, tzOffsetMinutes, useAsync,
} from "./ui";

const GOAL_KEY = (cid) => `prepaired.goal.${cid}`;
const PLAN_KEY = (cid) => `prepaired.plan.${cid}`;

function readJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}
function writeJSON(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* storage unavailable */ }
}

function greeting(name) {
  const h = new Date().getHours();
  const part = h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
  const first = (name || "").trim().split(/\s+/)[0];
  return first ? `${part}, ${first}` : part;
}

/** Topics and pinned questions for "Practice weak areas", derived only from measured data. */
export function weakAreaTargets(data) {
  const topics = [];
  const questionIds = [];
  (data?.topics || [])
    .filter((t) => t.band === "needs_work" && t.attempts >= 2)
    .slice(0, 3)
    .forEach((t) => topics.push(t.topic));
  (data?.declining_topics || []).forEach((t) => { if (!topics.includes(t.topic)) topics.push(t.topic); });
  (data?.revise_first || []).forEach((c) => {
    if (c.topic && !topics.includes(c.topic)) topics.push(c.topic);
    const q = c.related_questions?.[0]?.question_id;
    if (q && !questionIds.includes(q)) questionIds.push(q);
  });
  return { topics: topics.slice(0, 4), questionIds: questionIds.slice(0, 4) };
}

function Kpi({ icon, label, value, sub, children }) {
  return (
    <div className="panel kpi">
      <div className="kpi-label"><Icon name={icon} size={16} />{label}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
      {children}
    </div>
  );
}

function TopicBars({ items, empty }) {
  if (!items.length) return <p className="small faint">{empty}</p>;
  return (
    <div>
      {items.map((t) => {
        const meta = BAND_META[t.band] || BAND_META.unknown;
        return (
          <div className="topic-bar" key={t.topic}>
            <span className="name" title={t.label}>{t.label}</span>
            <Meter value={t.avg_score} tone={meta.tone} label={`${t.label} average`} className={t.low_data ? "hatch" : ""} />
            <span className="val">
              {pct(t.avg_score)} <span className="faint">· {t.attempts}×{t.low_data ? " low data" : ""}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}

function PrepPlan({ candidateId, topics }) {
  const [plan, setPlan] = useState(() => readJSON(PLAN_KEY(candidateId), { date: "", minutes: 30 }));
  const update = (patch) => { const next = { ...plan, ...patch }; setPlan(next); writeJSON(PLAN_KEY(candidateId), next); };

  const daysLeft = plan.date ? Math.ceil((new Date(plan.date + "T23:59:59") - new Date()) / 86400000) : null;
  const focus = topics.filter((t) => t.band !== "strong").sort((a, b) => (a.avg_score ?? 1) - (b.avg_score ?? 1));

  const weeks = useMemo(() => {
    if (daysLeft === null || daysLeft < 1 || !focus.length) return [];
    const nWeeks = Math.min(6, Math.max(1, Math.ceil(daysLeft / 7)));
    const perWeek = Math.ceil(focus.length / nWeeks);
    return Array.from({ length: nWeeks }, (_, i) => focus.slice(i * perWeek, (i + 1) * perWeek)).filter((w) => w.length);
  }, [daysLeft, focus]);

  return (
    <section className="panel" aria-labelledby="plan-h">
      <div className="panel-head">
        <div>
          <h3 id="plan-h">Preparation planner</h3>
          <p>Rule-based suggestion from your measured topic averages. It is not a prediction of interview results.</p>
        </div>
        <Icon name="calendar" size={18} />
      </div>
      <div className="row wrap" style={{ marginBottom: 12 }}>
        <label className="small muted" htmlFor="plan-date">Interview date</label>
        <input id="plan-date" className="field" type="date" value={plan.date} min={new Date().toISOString().slice(0, 10)}
          onChange={(e) => update({ date: e.target.value })} />
        <label className="small muted" htmlFor="plan-min">Minutes per day</label>
        <select id="plan-min" className="select" value={plan.minutes} onChange={(e) => update({ minutes: Number(e.target.value) })}>
          {[15, 30, 45, 60, 90].map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>
      {daysLeft === null && <p className="small faint">Add a target date to get a week-by-week focus order.</p>}
      {daysLeft !== null && daysLeft < 1 && <p className="small faint">That date has passed. Pick a future date.</p>}
      {daysLeft !== null && daysLeft >= 1 && !focus.length && (
        <p className="small faint">No weak or developing topics are measured yet. Complete more answers to build a plan.</p>
      )}
      {weeks.length > 0 && (
        <div className="stack" style={{ gap: 10 }}>
          <p className="small muted">{daysLeft} days left. About {Math.round((plan.minutes * 7) / 60 * 10) / 10} h of practice per week at {plan.minutes} min/day.</p>
          {weeks.map((w, i) => (
            <div key={i} className="step-card">
              <span className="icon-wrap"><Icon name="target" size={16} /></span>
              <div>
                <h4>Week {i + 1}</h4>
                <p>Focus: {w.map((t) => `${t.label} (${pct(t.avg_score)})`).join(", ")}. Finish with one pass over your most-missed concepts.</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default function Dashboard({ navigate }) {
  const { candidate, setSession } = useContext(SessionContext);
  const cid = candidate?.id;
  const { loading, data, error, reload } = useAsync(() => api.getDashboard(cid, tzOffsetMinutes()), [cid]);
  const [busy, setBusy] = useState("");
  const [actionError, setActionError] = useState("");
  const [goal, setGoal] = useState(() => readJSON(GOAL_KEY(cid), 3));

  const setGoalValue = (n) => { const v = Math.max(1, Math.min(14, n)); setGoal(v); writeJSON(GOAL_KEY(cid), v); };

  const launch = async (label, fn) => {
    setBusy(label); setActionError("");
    try {
      const created = await fn();
      setSession(created);
      navigate("interview");
    } catch (e) {
      setActionError(e.message || "Could not start the session.");
    } finally {
      setBusy("");
    }
  };

  const targets = useMemo(() => weakAreaTargets(data), [data]);
  const canPractice = targets.topics.length > 0;
  const hasHistory = !!data?.has_history;

  const onContinue = () => launch("continue", () => repeatLastSetup({ candidate, config: data.last_session_config }));
  const onPracticeWeak = () => launch("weak", () => startPractice({ candidate, topics: targets.topics, focusQuestionIds: targets.questionIds }));

  const runStep = (step) => {
    if (step.kind === "practice_topics") {
      return launch("step", () => startPractice({ candidate, topics: step.topics }));
    }
    if (step.kind === "compare") {
      try { localStorage.setItem("prepaired.compareQ", String(step.question_id)); } catch { /* ignore */ }
      return navigate("analytics");
    }
    if (step.kind === "weakness_map") return navigate("weakness");
    return navigate("topics");
  };

  const actions = (
    <>
      <button type="button" className="btn btn-ghost" onClick={onContinue}
        disabled={!!busy || !data?.last_session_config}
        title={data?.last_session_config ? "Start a new session with the topics of your last one" : "Available after your first session"}>
        {busy === "continue" ? <span className="spinner" /> : <Icon name="refresh" size={16} />} Continue practicing
      </button>
      <button type="button" className="btn btn-ghost" onClick={onPracticeWeak}
        disabled={!!busy || !canPractice}
        title={canPractice ? "Targets your measured weak topics and most-missed concepts" : "Needs at least two scored answers in a topic"}>
        {busy === "weak" ? <span className="spinner" /> : <Icon name="target" size={16} />} Practice weak areas
      </button>
      <button type="button" className="btn btn-primary" onClick={() => navigate("topics")} disabled={!!busy}>
        <Icon name="play" size={16} /> Start interview
      </button>
    </>
  );

  const subtitle = loading
    ? "Loading your progress…"
    : hasHistory
      ? `${data.totals.sessions_with_answers} session${data.totals.sessions_with_answers === 1 ? "" : "s"} with answers · last active ${formatDate(data.streak.last_active, { month: "short", day: "numeric", year: "numeric" })}`
      : "Answer a few questions and your progress will appear here.";

  return (
    <Shell page="dashboard" navigate={navigate} title={greeting(candidate?.name)} subtitle={subtitle} actions={actions}>
      {actionError && <div className="toast" role="alert" style={{ marginBottom: 14 }}>{actionError}</div>}
      {error && <div className="panel"><ErrorState error={error} onRetry={reload} what="your dashboard" /></div>}

      {loading && (
        <div className="stack" aria-busy="true" aria-live="polite">
          <div className="grid grid-4">{[0, 1, 2, 3].map((i) => <div key={i} className="panel"><Skeleton height={14} width="50%" /><Skeleton height={30} width="40%" style={{ marginTop: 12 }} /></div>)}</div>
          <div className="panel"><Skeleton height={190} /></div>
        </div>
      )}

      {data && (
        <div className="stack">
          <div className="grid grid-4">
            <Kpi icon="list" label="Questions attempted" value={data.totals.questions_attempted}
              sub={`${data.totals.primary_attempts} answers · ${data.totals.followups_answered} follow-ups`} />
            <Kpi icon="check" label="Completed sessions" value={data.totals.sessions_completed}
              sub={`${data.totals.sessions_with_answers} with answers · ${data.totals.sessions_started} started`} />
            <Kpi icon="chart" label="Average score" value={pct(data.totals.avg_score)}
              sub={data.totals.best_score !== null ? `Best answer ${pct(data.totals.best_score)}` : "No scored answers yet"}>
              {data.totals.avg_score !== null && (
                <Badge tone={BAND_META[bandOf(data.totals.avg_score)].tone}>{BAND_META[bandOf(data.totals.avg_score)].label}</Badge>
              )}
            </Kpi>
            <Kpi icon="flame" label="Practice streak"
              value={`${data.streak.current_days} day${data.streak.current_days === 1 ? "" : "s"}`}
              sub={`Longest ${data.streak.longest_days} · ${data.week.active_days} active day${data.week.active_days === 1 ? "" : "s"} this week`} />
          </div>

          <div className="grid grid-main">
            <section className="panel" aria-labelledby="trend-h">
              <div className="panel-head">
                <div>
                  <h3 id="trend-h">Score trend</h3>
                  <p>Average validated score per session with answers</p>
                </div>
                {data.recent_vs_earlier && <TrendChip cmp={data.recent_vs_earlier} />}
              </div>
              {data.score_trend.length === 0 ? (
                <EmptyState icon="chart" title="No scored sessions yet"
                  action={<button type="button" className="btn btn-primary btn-sm" onClick={() => navigate("topics")}>Start your first interview</button>}>
                  Scores appear after you answer questions in a session.
                </EmptyState>
              ) : (
                <>
                  <LineChart ariaLabel="Average score per session"
                    points={data.score_trend.map((p) => ({ label: formatDate(p.date), value: p.avg_score ?? 0, detail: `${p.answered} answer${p.answered === 1 ? "" : "s"}` }))} />
                  <div className="legend" style={{ marginTop: 8 }}><span><i />Dashed lines: evaluator “Average” (40%) and “Good” (60%) boundaries</span></div>
                </>
              )}
            </section>

            <section className="panel" aria-labelledby="week-h">
              <div className="panel-head">
                <div><h3 id="week-h">This week</h3><p>Last 7 days, your timezone</p></div>
                <span className="row">
                  <button type="button" className="icon-btn" aria-label="Lower weekly goal" onClick={() => setGoalValue(goal - 1)}>−</button>
                  <button type="button" className="icon-btn" aria-label="Raise weekly goal" onClick={() => setGoalValue(goal + 1)}>+</button>
                </span>
              </div>
              <div className="row-between"><span className="kpi-value">{data.week.sessions}<span className="faint" style={{ fontSize: 16 }}> / {goal}</span></span>
                <span className="small muted">sessions (your goal)</span></div>
              <Meter value={Math.min(1, data.week.sessions / goal)} tone={data.week.sessions >= goal ? "success" : "accent"} label="Weekly goal progress" height={10} />
              <p className="small faint" style={{ marginTop: 10 }}>
                {data.week.attempts} answered question{data.week.attempts === 1 ? "" : "s"} this week.
                {data.week.sessions >= goal ? " Goal reached." : ` ${goal - data.week.sessions} more session${goal - data.week.sessions === 1 ? "" : "s"} to reach your goal.`}
              </p>
            </section>
          </div>

          <div className="grid grid-2">
            <section className="panel" aria-labelledby="topics-h">
              <div className="panel-head">
                <div><h3 id="topics-h">Topic strengths and weaknesses</h3><p>Average score per topic. Hatched bars rest on fewer than 3 attempts.</p></div>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate("analytics")}>Details</button>
              </div>
              {data.topics.length === 0 ? (
                <p className="small faint">Topic results appear after you answer questions.</p>
              ) : (
                <div className="stack" style={{ gap: 14 }}>
                  <div>
                    <div className="small muted" style={{ marginBottom: 4 }}>Needs attention</div>
                    <TopicBars items={data.topics.filter((t) => t.band === "needs_work").slice(0, 4)} empty="No topic is below the 40% boundary." />
                  </div>
                  <div>
                    <div className="small muted" style={{ marginBottom: 4 }}>Strongest</div>
                    <TopicBars items={[...data.topics].filter((t) => t.band === "strong").sort((a, b) => b.avg_score - a.avg_score).slice(0, 4)} empty="No topic is at or above the 60% boundary yet." />
                  </div>
                </div>
              )}
            </section>

            <section className="panel" aria-labelledby="next-h">
              <div className="panel-head"><div><h3 id="next-h">What to do next</h3><p>Suggested from your stored attempts</p></div></div>
              <div className="stack" style={{ gap: 10 }}>
                {data.next_steps.map((s, i) => (
                  <div key={i} className="step-card">
                    <span className="icon-wrap"><Icon name={s.kind === "weakness_map" ? "target" : s.kind === "compare" ? "compare" : "play"} size={16} /></span>
                    <div className="grow" style={{ flex: 1, minWidth: 0 }}>
                      <h4>{s.title}</h4>
                      <p>{s.detail}</p>
                    </div>
                    <button type="button" className="btn btn-ghost btn-sm" onClick={() => runStep(s)} disabled={!!busy} aria-label={`${s.title}: go`}>
                      <Icon name="arrow" size={14} />
                    </button>
                  </div>
                ))}
              </div>
              {data.revise_first.length > 0 && (
                <>
                  <div className="small muted" style={{ margin: "16px 0 6px" }}>Most-missed concepts</div>
                  <div className="list">
                    {data.revise_first.map((c) => (
                      <div className="list-row" key={c.key}>
                        <span className="grow"><span className="row-title clamp-2" style={{ fontWeight: 500 }}>{c.concept}</span>
                          <span className="row-sub">Missed {c.missing} of {c.observations} observations</span></span>
                      </div>
                    ))}
                  </div>
                  <button type="button" className="btn btn-ghost btn-sm" style={{ marginTop: 10 }} onClick={() => navigate("weakness")}>Open Weakness Map</button>
                </>
              )}
            </section>
          </div>

          <div className="grid grid-2">
            <section className="panel" aria-labelledby="recent-h">
              <div className="panel-head"><div><h3 id="recent-h">Recent sessions</h3><p>Newest first</p></div></div>
              {data.recent_sessions.length === 0 ? <p className="small faint">No sessions yet.</p> : (
                <div className="list">
                  {data.recent_sessions.slice(0, 6).map((s) => (
                    <div className="list-row" key={s.id}>
                      <span className="avatar" style={{ width: 30, height: 30, fontSize: 11, background: "var(--surface-2)", color: "var(--text-2)" }}>{s.answered}</span>
                      <span className="grow">
                        <span className="row-title clamp-1">{s.topics.length ? s.topics.map((t) => t.replace(/_/g, " ")).join(", ") : "Mixed topics"}</span>
                        <span className="row-sub">{formatDate(s.created_at, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })} · {s.mode === "demo_rl" ? "Demo interview" : "Standard"} · {s.answered}/{s.planned_questions} answered</span>
                      </span>
                      {s.has_activity
                        ? <Badge tone={BAND_META[bandOf(s.avg_score)].tone}>{pct(s.avg_score)}</Badge>
                        : <Badge tone="neutral">No answers</Badge>}
                    </div>
                  ))}
                </div>
              )}
            </section>

            <PrepPlan candidateId={cid} topics={data.topics} />
          </div>

          {!hasHistory && (
            <div className="notice"><Icon name="info" size={16} /><span>This dashboard only shows what you have actually answered. Nothing is estimated before your first session.</span></div>
          )}
        </div>
      )}
    </Shell>
  );
}

function bandOf(score) {
  if (score === null || score === undefined) return "unknown";
  return score >= 0.6 ? "strong" : score >= 0.4 ? "developing" : "needs_work";
}

function TrendChip({ cmp }) {
  const up = cmp.delta > 0.005, down = cmp.delta < -0.005;
  return (
    <Badge tone={up ? "success" : down ? "danger" : "neutral"}
      title={`Average of the last ${cmp.recent_sessions} sessions vs the ${cmp.earlier_sessions} before them`}>
      <Icon name={up ? "up" : down ? "down" : "arrow"} size={12} />
      {up ? "+" : ""}{Math.round(cmp.delta * 100)} pts vs earlier
    </Badge>
  );
}
