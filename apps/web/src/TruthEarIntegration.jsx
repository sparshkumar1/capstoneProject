import Topbar from "./Topbar";

const TRUTH_EAR_URL = "https://truth-ear.lovable.app/";

export default function TruthEarIntegration({ navigate }) {
  return (
    <div className="page" style={{ background: "var(--bg)" }}>
      <Topbar navigate={navigate} />

      <div style={{ maxWidth: 1240, margin: "0 auto", padding: "24px 24px 40px" }}>
        <div className="card" style={{ padding: 20, marginBottom: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
            <div>
              <h2 style={{ fontFamily: "Syne", fontSize: 22, marginBottom: 6 }}>Voice Agent Integration</h2>
              <p style={{ color: "var(--text-2)", fontSize: 13 }}>
                Embedded from truth-ear.lovable.app. If embedding is blocked by browser security headers,
                open it in a new tab.
              </p>
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate("topics")}>Back to Topics</button>
              <a className="btn btn-primary btn-sm" href={TRUTH_EAR_URL} target="_blank" rel="noreferrer">Open in New Tab</a>
            </div>
          </div>
        </div>

        <div className="card" style={{ overflow: "hidden", minHeight: "72vh" }}>
          <iframe
            title="Truth Ear Voice Agent"
            src={TRUTH_EAR_URL}
            style={{ width: "100%", height: "72vh", border: "none", background: "var(--bg)" }}
            referrerPolicy="strict-origin-when-cross-origin"
            allow="microphone; clipboard-read; clipboard-write"
          />
        </div>
      </div>
    </div>
  );
}
