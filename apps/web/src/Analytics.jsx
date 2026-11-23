import { useContext, useEffect, useState } from "react";
import { SessionContext } from "./contexts";
import Shell from "./Shell";
import { api } from "./api";
import { BAND_META, Badge, EmptyState, ErrorState, Icon, LineChart, Meter, Skeleton, formatDate, formatDateTime, pct, tzOffsetMinutes, useAsync } from "./ui";

function Delta({ value }) {
  if (value === null || value === undefined) return <span className="faint">—</span>;
  const pts = Math.round(value * 100);
  return <Badge tone={pts > 0 ? "success" : pts < 0 ? "danger" : "neutral"}>{pts > 0 ? "+" : ""}{pts} pts</Badge>;
}

function ConceptList({ title, items, tone }) {
  if (!items?.length) return null;
  return (
    <div>
      <div className="small muted" style={{ marginBottom: 4 }}>{title}</div>
      <div className="tag-list">{items.map((t, i) => <span key={i} className={`tag ${tone}`}>{t}</span>)}</div>
    </div>
  );
}

function ComparePanel({ candidateId, questionId, onClose }) {
  const { loading, data, error, reload } = useAsync(() => api.compareAttempts(candidateId, questionId), [candidateId, questionId]);
  const s = data?.summary;
  const first = data?.attempts?.[0];
  const last = data?.attempts?.[data.attempts.length - 1];
  return (
    <section className="panel" aria-labelledby="cmp-h" id="compare-panel">
      <div className="panel-head">
        <div><h3 id="cmp-h">Compare attempts</h3><p className="clamp-2">{data?.question?.text || `Question ${questionId}`}</p></div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Close comparison"><Icon name="x" size={16} /></button>
      </div>
      {loading && <Skeleton height={120} />}
      {error && <ErrorState error={error} onRetry={reload} what="this comparison" />}
      {data && data.attempts.length < 2 && <p className="small faint">Answer this question at least twice to compare attempts.</p>}
      {data && data.attempts.length >= 2 && (
        <div className="stack">
          <div className="row wrap">
            {data.attempts.map((a) => (
              <Badge key={a.n} tone={BAND_META[a.score === null ? "unknown" : a.score >= 0.6 ? "strong" : a.score >= 0.4 ? "developing" : "needs_work"].tone}
                title={formatDateTime(a.created_at)}>#{a.n}: {pct(a.score)}</Badge>
            ))}
            <span className="small muted">First → latest</span><Delta value={s.delta} />
          </div>
          <div className="grid grid-3">
            <ConceptList title="Recovered in latest attempt" items={s.recovered_concepts} tone="good" />
            <ConceptList title="Missed repeatedly" items={s.repeated_missing} tone="bad" />
            <ConceptList title="Newly missed" items={s.newly_missed} tone="warn" />
          </div>
          {!s.recovered_concepts.length && !s.repeated_missing.length && !s.newly_missed.length && (
            <p className="small faint">No concept-level changes recorded between these attempts.</p>
          )}
          <div className="diff-cols">
            {[["First answer", first, s.answer_words_first], ["Latest answer", last, s.answer_words_latest]].map(([label, a, words]) => (
              <div key={label}>
                <div className="row-between" style={{ marginBottom: 6 }}>
                  <strong className="small">{label}</strong>
                  <span className="small faint">{pct(a.score)} · {words} words</span>
                </div>
                <div className="answer-box">{a.answer || "No transcript recorded for this attempt."}</div>
                <ConceptList title="Still missing" items={a.missing} tone="bad" />
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

export default function Analytics({ navigate }) {
  const { candidate } = useContext(SessionContext);
  const cid = candidate?.id;
  const { loading, data, error, reload } = useAsync(() => api.getAnalytics(cid, tzOffsetMinutes()), [cid]);
  const [compareQ, setCompareQ] = useState(null);

  // A concept/next-step link can hand over a question id to open straight away.
  useEffect(() => {
    try {
      const q = localStorage.getItem("prepaired.compareQ");
      if (q) { setCompareQ(q); localStorage.removeItem("prepaired.compareQ"); }
    } catch { /* ignore */ }
  }, []);
  useEffect(() => {
    if (compareQ) document.getElementById("compare-panel")?.scrollIntoView?.({ behavior: "smooth", block: "start" });
  }, [compareQ, data]);

  const empty = data && !data.has_history;
  return (
    <Shell page="analytics" navigate={navigate} title="Progress & analytics"
      subtitle="Everything here is computed from your stored answers and evaluator scores">
      {error && <div className="panel"><ErrorState error={error} onRetry={reload} what="your analytics" /></div>}
      {loading && <div className="panel" aria-busy="true"><Skeleton height={220} /></div>}
      {empty && (
        <div className="panel">
          <EmptyState icon="chart" title="No answers recorded yet"
            action={<button type="button" className="btn btn-primary btn-sm" onClick={() => navigate("topics")}>Start an interview</button>}>
            Charts appear once you have answered questions.
          </EmptyState>
        </div>
      )}
      {data && !empty && (
        <div className="stack">
          <section className="panel" aria-labelledby="time-h">
            <div className="panel-head">
              <div><h3 id="time-h">Performance over time</h3><p>Each point is one scored answer, oldest to newest</p></div>
              {data.recent_vs_earlier && (
                <span className="small muted">Last {data.recent_vs_earlier.recent_sessions} sessions {pct(data.recent_vs_earlier.recent_avg)} vs {pct(data.recent_vs_earlier.earlier_avg)} before <Delta value={data.recent_vs_earlier.delta} /></span>
              )}
            </div>
            {data.attempt_timeline.length === 0
              ? <p className="small faint">No scored answers yet.</p>
              : <LineChart ariaLabel="Score for each answered question"
                  points={data.attempt_timeline.map((t) => ({ label: formatDate(t.date), value: t.score, detail: `${t.topic.replace(/_/g, " ")}${t.difficulty ? ` · difficulty ${t.difficulty}` : ""}` }))} />}
          </section>

          <div className="grid grid-2">
            <section className="panel" aria-labelledby="mastery-h">
              <div className="panel-head"><div><h3 id="mastery-h">Topic mastery</h3><p>Average score; hatched = under 3 attempts</p></div></div>
              {data.topics.map((t) => (
                <div className="topic-bar" key={t.topic}>
                  <span className="name" title={t.label}>{t.label}</span>
                  <Meter value={t.avg_score} tone={BAND_META[t.band].tone === "warn" ? "warn" : BAND_META[t.band].tone} label={`${t.label} average`} />
                  <span className="val">{pct(t.avg_score)} <span className="faint">· {t.attempts}×</span></span>
                </div>
              ))}
              {data.topics.length === 0 && <p className="small faint">No scored topic attempts yet.</p>}
            </section>

            <div className="stack">
              <section className="panel" aria-labelledby="diff-h">
                <div className="panel-head"><div><h3 id="diff-h">By difficulty</h3><p>Average score at each question difficulty (1–5)</p></div></div>
                {data.difficulty.length === 0 ? <p className="small faint">No difficulty data yet.</p> : data.difficulty.map((d) => (
                  <div className="topic-bar" key={d.level}>
                    <span className="name">Level {d.level}</span>
                    <Meter value={d.avg_score} tone={BAND_META[d.avg_score >= 0.6 ? "strong" : d.avg_score >= 0.4 ? "developing" : "needs_work"].tone} label={`Difficulty ${d.level}`} />
                    <span className="val">{pct(d.avg_score)} <span className="faint">· {d.attempts}×</span></span>
                  </div>
                ))}
              </section>
              <section className="panel" aria-labelledby="type-h">
                <div className="panel-head"><div><h3 id="type-h">By answer type</h3><p>Spoken vs code answers</p></div></div>
                <div className="list">
                  {data.by_answer_type.map((t) => (
                    <div className="list-row" key={t.answer_type}>
                      <Icon name={t.answer_type === "code" ? "code" : "mic"} size={16} />
                      <span className="grow row-title">{t.answer_type === "code" ? "Code" : "Verbal"}</span>
                      <span className="small muted">{t.attempts} answers</span>
                      <Badge tone={BAND_META[t.avg_score >= 0.6 ? "strong" : t.avg_score >= 0.4 ? "developing" : "needs_work"].tone}>{pct(t.avg_score)}</Badge>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>

          <section className="panel" aria-labelledby="comp-h">
            <div className="panel-head"><div><h3 id="comp-h">Questions you have retried</h3><p>Pick one to compare your attempts side by side</p></div></div>
            {data.comparable_questions.length === 0 ? (
              <p className="small faint">No question has been answered twice yet. Retry a question to see how your answers change.</p>
            ) : (
              <div className="list">
                {data.comparable_questions.map((q) => (
                  <button key={q.question_id} type="button" className={`row-btn ${compareQ === q.question_id ? "selected" : ""}`}
                    onClick={() => setCompareQ(q.question_id)}>
                    <span className="grow" style={{ textAlign: "left", minWidth: 0 }}>
                      <span className="row-title clamp-2">{q.text || `Question ${q.question_id}`}</span>
                      <span className="row-sub">{q.topic.replace(/_/g, " ")} · {q.attempts} attempts · best {pct(q.best_score)}</span>
                    </span>
                    <Delta value={q.delta} />
                  </button>
                ))}
              </div>
            )}
          </section>

          {compareQ && <ComparePanel candidateId={cid} questionId={compareQ} onClose={() => setCompareQ(null)} />}
        </div>
      )}
    </Shell>
  );
}
