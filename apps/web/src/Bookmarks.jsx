import { useContext, useState } from "react";
import { SessionContext } from "./contexts";
import Shell from "./Shell";
import { api } from "./api";
import { startPractice } from "./practice";
import { Badge, EmptyState, ErrorState, Icon, Skeleton, formatDate, useAsync } from "./ui";

function NoteEditor({ bookmark, candidateId, onSaved }) {
  const [editing, setEditing] = useState(false);
  const [note, setNote] = useState(bookmark.note || "");
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      await api.addBookmark(candidateId, bookmark.question_id, note);
      onSaved(note);
      setEditing(false);
    } catch (err) {
      console.error("[Bookmarks] note save failed:", err);
    } finally {
      setSaving(false);
    }
  };

  if (!editing) {
    return (
      <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEditing(true)} style={{ fontSize: 12 }}>
        <Icon name="list" size={13} /> {bookmark.note ? "Edit note" : "Add note"}
      </button>
    );
  }

  return (
    <div className="row wrap" style={{ gap: 6, marginTop: 6 }}>
      <textarea
        className="input"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Why did you bookmark this question?"
        rows={2}
        style={{ flex: "1 1 220px", resize: "vertical", fontFamily: "inherit", fontSize: 13 }}
      />
      <button type="button" className="btn btn-primary btn-sm" disabled={saving} onClick={save}>
        {saving ? "Saving…" : "Save"}
      </button>
      <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setNote(bookmark.note || ""); setEditing(false); }}>
        Cancel
      </button>
    </div>
  );
}

export default function Bookmarks({ navigate }) {
  const { candidate, setSession } = useContext(SessionContext);
  const cid = candidate?.id;
  const { loading, data, error, reload } = useAsync(() => api.getBookmarks(cid), [cid]);
  const [busyId, setBusyId] = useState(null);
  const [actionError, setActionError] = useState("");

  const bookmarks = data?.bookmarks || [];

  const remove = async (questionId) => {
    setBusyId(questionId);
    try {
      await api.removeBookmark(cid, questionId);
      reload();
    } catch (err) {
      setActionError(err.message || "Could not remove bookmark.");
    } finally {
      setBusyId(null);
    }
  };

  const practice = async (bookmark) => {
    setBusyId(bookmark.question_id);
    setActionError("");
    try {
      const created = await startPractice({
        candidate,
        topics: bookmark.topic ? [bookmark.topic] : [],
        focusQuestionIds: [bookmark.question_id],
        numQuestions: 3,
      });
      setSession(created);
      navigate("interview");
    } catch (err) {
      setActionError(err.message || "Could not start the session.");
    } finally {
      setBusyId(null);
    }
  };

  return (
    <Shell
      page="bookmarks"
      navigate={navigate}
      title="Bookmarks"
      subtitle="Questions you've flagged to revisit, with your own notes."
    >
      {actionError && <div className="banner banner-danger" style={{ marginBottom: 12 }}>{actionError}</div>}

      {loading && (
        <div className="panel-grid">
          {[0, 1, 2].map((i) => <Skeleton key={i} height={96} />)}
        </div>
      )}

      {!loading && error && <ErrorState error={error} onRetry={reload} what="your bookmarks" />}

      {!loading && !error && bookmarks.length === 0 && (
        <EmptyState icon="bookmark" title="No bookmarks yet">
          Bookmark a question from your report or weakness map to revisit it here later.
        </EmptyState>
      )}

      {!loading && !error && bookmarks.length > 0 && (
        <div className="card-list">
          {bookmarks.map((b) => (
            <div key={b.id} className="card list-row" style={{ flexDirection: "column", alignItems: "stretch", gap: 8 }}>
              <div className="row wrap" style={{ justifyContent: "space-between" }}>
                <div style={{ flex: "1 1 320px" }}>
                  <div className="row wrap" style={{ gap: 6, marginBottom: 4 }}>
                    {b.topic && <Badge tone="neutral">{b.topic.replace(/_/g, " ")}</Badge>}
                    {b.difficulty != null && <Badge tone="accent">Difficulty {b.difficulty}</Badge>}
                    <span className="small muted">Bookmarked {formatDate(b.created_at)}</span>
                  </div>
                  <p style={{ fontWeight: 500, margin: 0 }}>{b.question_text || `Question ${b.question_id}`}</p>
                </div>
                <div className="row" style={{ gap: 6 }}>
                  <button type="button" className="btn btn-primary btn-sm" disabled={busyId === b.question_id} onClick={() => practice(b)}>
                    <Icon name="play" size={13} /> Practice this
                  </button>
                  <button type="button" className="icon-btn" disabled={busyId === b.question_id} onClick={() => remove(b.question_id)}
                    aria-label="Remove bookmark" title="Remove bookmark">
                    <Icon name="x" size={15} />
                  </button>
                </div>
              </div>
              {b.note && <p className="small" style={{ background: "var(--surface-2)", borderRadius: 8, padding: "8px 10px", margin: 0 }}>{b.note}</p>}
              <NoteEditor bookmark={b} candidateId={cid} onSaved={reload} />
            </div>
          ))}
        </div>
      )}
    </Shell>
  );
}
