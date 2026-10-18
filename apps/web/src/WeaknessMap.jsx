import { useContext, useMemo, useState } from "react";
import { SessionContext } from "./contexts";
import Shell from "./Shell";
import { api } from "./api";
import { startPractice } from "./practice";
import { Badge, EmptyState, ErrorState, Icon, Meter, OutcomeDots, Skeleton, formatDate, pct, useAsync } from "./ui";

const CLASS_META = {
  frequently_missed: { label: "Frequently missed", tone: "danger", meter: "danger" },
  partial: { label: "Partial", tone: "warn", meter: "warn" },
  strong: { label: "Strong", tone: "success", meter: "success" },
  not_enough_data: { label: "Need more data", tone: "neutral", meter: "neutral" },
};
const FILTERS = [
  { id: "all", label: "All" },
  { id: "frequently_missed", label: "Frequently missed" },
  { id: "partial", label: "Partial" },
  { id: "strong", label: "Strong" },
  { id: "not_enough_data", label: "Need more data" },
];
const RATING_KEY = (cid) => `prepaired.cardRatings.${cid}`;

function readRatings(cid) {
  try { return JSON.parse(localStorage.getItem(RATING_KEY(cid)) || "{}"); } catch { return {}; }
}

function RevisionCard({ card, rating, onRate }) {
  const [flipped, setFlipped] = useState(false);
  return (
    <div>
      <div className={`flip ${flipped ? "flipped" : ""}`}>
        <div className="flip-inner">
          <div className="flip-face" aria-hidden={flipped}>
            <Badge tone="accent">Recall</Badge>
            <p style={{ fontWeight: 500 }}>{card.recall_prompt}</p>
            <p className="small muted">Concept you tend to miss: <strong>{card.concept}</strong></p>
            <button type="button" className="btn btn-ghost btn-sm" style={{ marginTop: "auto", alignSelf: "flex-start" }}
              onClick={() => setFlipped(true)} tabIndex={flipped ? -1 : 0}>
              <Icon name="flip" size={14} /> Show reference
            </button>
          </div>
          <div className="flip-face flip-back" aria-hidden={!flipped}>
            <Badge tone="neutral">From question rubric</Badge>
            <p className="small" style={{ whiteSpace: "pre-wrap" }}>{card.reference || "No reference answer stored for this question."}</p>
            {card.common_mistakes.length > 0 && (
              <div className="tag-list">
                {card.common_mistakes.map((m, i) => <span key={i} className="tag bad">Common mistake: {m}</span>)}
              </div>
            )}
            <button type="button" className="btn btn-ghost btn-sm" style={{ marginTop: "auto", alignSelf: "flex-start" }}
              onClick={() => setFlipped(false)} tabIndex={flipped ? 0 : -1}>
              <Icon name="flip" size={14} /> Back
            </button>
          </div>
        </div>
      </div>
      <div className="row wrap" style={{ marginTop: 8 }}>
        <span className="small muted">How well did you recall it?</span>
        {[["again", "Not yet"], ["ok", "Mostly"], ["good", "Solid"]].map(([id, label]) => (
          <button key={id} type="button" className="chip" aria-pressed={rating === id} onClick={() => onRate(id)}>{label}</button>
        ))}
      </div>
    </div>
  );
}

function ConceptDetail({ concept, onClose, onPractice, onCompare, busy, cid }) {
  const [ratings, setRatings] = useState(() => readRatings(cid));
  const rate = (id) => {
    const next = { ...ratings, [concept.key]: id };
    setRatings(next);
    try { localStorage.setItem(RATING_KEY(cid), JSON.stringify(next)); } catch { /* ignore */ }
  };
  const meta = CLASS_META[concept.classification];
  return (
    <aside className="panel drawer" aria-label={`Details for ${concept.concept}`}>
      <div className="panel-head">
        <div>
          <h3 className="clamp-2">{concept.concept}</h3>
          <p>{concept.topic.replace(/_/g, " ")}</p>
        </div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Close details"><Icon name="x" size={16} /></button>
      </div>
      <div className="row wrap" style={{ marginBottom: 10 }}>
        <Badge tone={meta.tone}>{meta.label}</Badge>
        {concept.low_data && <Badge tone="neutral" title="Fewer than 3 observations">Low data</Badge>}
        <span className="small muted">Covered {concept.covered} · missed {concept.missing}</span>
        <OutcomeDots recent={concept.recent} />
      </div>

      <div className="small muted" style={{ margin: "6px 0" }}>Questions where this showed up</div>
      <div className="list">
        {concept.related_questions.map((q) => (
          <div className="list-row" key={q.question_id}>
            <span className="grow">
              <span className="row-title clamp-2">{q.text || `Question ${q.question_id}`}</span>
              <span className="row-sub">{q.attempts} attempt{q.attempts === 1 ? "" : "s"}{q.best_score !== null ? ` · best ${pct(q.best_score)}` : ""}</span>
            </span>
            {q.attempts >= 2 && (
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => onCompare(q.question_id)}>
                <Icon name="compare" size={14} /> Compare
              </button>
            )}
          </div>
        ))}
      </div>

      <button type="button" className="btn btn-primary" style={{ margin: "14px 0" }} disabled={busy}
        onClick={() => onPractice(concept)}>
        {busy ? <span className="spinner" /> : <Icon name="target" size={16} />} Practice this concept
      </button>
      <p className="small faint" style={{ marginTop: -6, marginBottom: 12 }}>
        Starts a short session on this topic with the related questions first. The interviewer may adapt later questions.
      </p>

      {concept.revision_card ? (
        <RevisionCard card={concept.revision_card} rating={ratings[concept.key]} onRate={rate} />
      ) : (
        <p className="small faint">Revision cards are generated for concepts you miss or only partly cover.</p>
      )}
    </aside>
  );
}

export default function WeaknessMap({ navigate }) {
  const { candidate, setSession } = useContext(SessionContext);
  const cid = candidate?.id;
  const { loading, data, error, reload } = useAsync(() => api.getWeaknessMap(cid), [cid]);
  const [filter, setFilter] = useState("all");
  const [topic, setTopic] = useState("all");
  const [selectedKey, setSelectedKey] = useState(null);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");

  const topics = useMemo(() => [...new Set((data?.concepts || []).map((c) => c.topic))].sort(), [data]);
  const visible = useMemo(
    () => (data?.concepts || []).filter((c) => (filter === "all" || c.classification === filter) && (topic === "all" || c.topic === topic)),
    [data, filter, topic],
  );
  const selected = (data?.concepts || []).find((c) => c.key === selectedKey) || null;

  const practice = async (concept) => {
    setBusy(true); setActionError("");
    try {
      const created = await startPractice({
        candidate,
        topics: [concept.topic],
        focusQuestionIds: concept.related_questions.map((q) => q.question_id),
      });
      setSession(created);
      navigate("interview");
    } catch (e) {
      setActionError(e.message || "Could not start the session.");
    } finally {
      setBusy(false);
    }
  };
  const compare = (qid) => {
    try { localStorage.setItem("prepaired.compareQ", String(qid)); } catch { /* ignore */ }
    navigate("analytics");
  };

  const s = data?.summary;
  return (
    <Shell page="weakness" navigate={navigate} title="My Weakness Map"
      subtitle="Concepts the evaluator found covered or missing in your spoken answers">
      {actionError && <div className="toast" role="alert" style={{ marginBottom: 14 }}>{actionError}</div>}
      {error && <div className="panel"><ErrorState error={error} onRetry={reload} what="your weakness map" /></div>}
      {loading && <div className="panel" aria-busy="true"><Skeleton height={16} width="40%" /><Skeleton height={120} style={{ marginTop: 14 }} /></div>}

      {data && (
        <div className="stack">
          <div className="notice">
            <Icon name="info" size={16} />
            <span>
              <strong>Measured, not estimated.</strong> Each concept is counted from stored evaluator results
              (covered vs missing). A concept is only classified after 2+ observations; fewer than 3 is marked low data.
              Code answers are excluded{s.code_attempts_excluded ? ` (${s.code_attempts_excluded} skipped)` : ""}.
            </span>
          </div>

          {s.concepts_tracked === 0 ? (
            <div className="panel">
              <EmptyState icon="target" title="No concept data yet"
                action={<button type="button" className="btn btn-primary btn-sm" onClick={() => navigate("topics")}>Start an interview</button>}>
                Answer verbal questions and the evaluator&apos;s covered and missing concepts will build your map.
              </EmptyState>
            </div>
          ) : (
            <>
              <div className="grid grid-4">
                <div className="panel kpi"><div className="kpi-label">Frequently missed</div><div className="kpi-value">{s.frequently_missed}</div></div>
                <div className="panel kpi"><div className="kpi-label">Partial</div><div className="kpi-value">{s.partial}</div></div>
                <div className="panel kpi"><div className="kpi-label">Strong</div><div className="kpi-value">{s.strong}</div></div>
                <div className="panel kpi"><div className="kpi-label">Need more data</div><div className="kpi-value">{s.not_enough_data}</div></div>
              </div>

              <div className={`split ${selected ? "has-detail" : ""}`}>
                <section className="panel" aria-labelledby="concepts-h">
                  <div className="panel-head">
                    <div><h3 id="concepts-h">Concepts</h3><p>{visible.length} of {data.concepts.length} shown · most missed first</p></div>
                    <select className="select" value={topic} onChange={(e) => setTopic(e.target.value)} aria-label="Filter by topic">
                      <option value="all">All topics</option>
                      {topics.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
                    </select>
                  </div>
                  <div className="chips" style={{ marginBottom: 12 }} role="group" aria-label="Filter by classification">
                    {FILTERS.map((f) => (
                      <button key={f.id} type="button" className="chip" aria-pressed={filter === f.id} onClick={() => setFilter(f.id)}>{f.label}</button>
                    ))}
                  </div>
                  {visible.length === 0 ? <p className="small faint">No concepts match these filters.</p> : (
                    <div className="list">
                      {visible.map((c) => {
                        const meta = CLASS_META[c.classification];
                        return (
                          <button key={c.key} type="button" className={`row-btn ${selectedKey === c.key ? "selected" : ""}`}
                            aria-pressed={selectedKey === c.key} onClick={() => setSelectedKey(c.key)}>
                            <span className="grow" style={{ minWidth: 0, textAlign: "left" }}>
                              <span className="row-title clamp-2" style={{ fontWeight: 500 }}>{c.concept}</span>
                              <span className="row-sub">{c.topic.replace(/_/g, " ")} · {c.observations} obs · last {formatDate(c.last_seen)}</span>
                              <Meter value={c.coverage_rate} tone={meta.meter} label={`${c.concept} coverage`} height={6} />
                            </span>
                            <span className="stack" style={{ gap: 4, alignItems: "flex-end" }}>
                              <Badge tone={meta.tone}>{meta.label}</Badge>
                              <OutcomeDots recent={c.recent} />
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </section>
                {selected && (
                  <ConceptDetail concept={selected} cid={cid} busy={busy}
                    onClose={() => setSelectedKey(null)} onPractice={practice} onCompare={compare} />
                )}
              </div>

              <div className="grid grid-2">
                <section className="panel" aria-labelledby="mis-h">
                  <div className="panel-head"><div><h3 id="mis-h">Repeated misconceptions</h3><p>Incorrect claims the evaluator flagged in your answers</p></div></div>
                  {data.misconceptions.length === 0 ? <p className="small faint">No incorrect claims recorded.</p> : (
                    <div className="list">
                      {data.misconceptions.slice(0, 8).map((m, i) => (
                        <div className="list-row" key={i}>
                          <span className="grow">
                            <span className="row-title clamp-2">{m.claim}</span>
                            <span className="row-sub">{m.topic.replace(/_/g, " ")} · last {formatDate(m.last_seen)}</span>
                          </span>
                          <Badge tone={m.times >= 2 ? "danger" : "neutral"}>{m.times}×</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
                <section className="panel" aria-labelledby="dec-h">
                  <div className="panel-head"><div><h3 id="dec-h">Declining topics</h3><p>Recent half of attempts scores 10+ points below the earlier half (needs 4+ attempts)</p></div></div>
                  {data.declining_topics.length === 0 ? <p className="small faint">No topic shows a measured decline.</p> : (
                    <div className="list">
                      {data.declining_topics.map((t) => (
                        <div className="list-row" key={t.topic}>
                          <Icon name="down" size={16} />
                          <span className="grow"><span className="row-title">{t.label}</span>
                            <span className="row-sub">{t.attempts} attempts · average {pct(t.avg_score)}</span></span>
                          <Badge tone="danger">{Math.round((t.trend_delta || 0) * 100)} pts</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              </div>
            </>
          )}
        </div>
      )}
    </Shell>
  );
}
