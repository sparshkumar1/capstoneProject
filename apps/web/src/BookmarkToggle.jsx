import { useState } from "react";
import { Icon } from "./ui";
import { api } from "./api";

/**
 * Controlled bookmark toggle button. The parent owns whether this question is
 * currently bookmarked (`bookmarked`) and is notified of changes (`onChange`)
 * so it can update whatever list/set it already loaded — this component only
 * makes the actual API call and shows local pending/error state.
 */
export default function BookmarkToggle({ candidateId, questionId, bookmarked, onChange, size = 16 }) {
  const [busy, setBusy] = useState(false);

  const toggle = async (e) => {
    e.stopPropagation();
    if (!candidateId || !questionId || busy) return;
    setBusy(true);
    try {
      if (bookmarked) {
        await api.removeBookmark(candidateId, questionId);
        onChange?.(false);
      } else {
        await api.addBookmark(candidateId, questionId, "");
        onChange?.(true);
      }
    } catch (err) {
      console.error("[Bookmark] toggle failed:", err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      className="icon-btn"
      onClick={toggle}
      disabled={busy}
      aria-pressed={bookmarked}
      aria-label={bookmarked ? "Remove bookmark" : "Bookmark this question"}
      title={bookmarked ? "Remove bookmark" : "Bookmark this question"}
      style={{ color: bookmarked ? "var(--accent-2)" : undefined }}
    >
      <Icon name={bookmarked ? "bookmarkFilled" : "bookmark"} size={size} />
    </button>
  );
}
