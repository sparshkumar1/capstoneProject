import { useState, useContext } from "react";
import { SessionContext } from "./contexts";
import Topbar from "./Topbar";
import { api } from "./api";
import "./TopicSelector.css";

const C_TOPICS = [
  { id: "pointers", label: "Pointers & Memory", icon: "🧭", desc: "Pointer arithmetic, double pointers, void pointers, memory leaks" },
  { id: "arrays_strings", label: "Arrays & Strings", icon: "📐", desc: "Multi-dim arrays, string manipulation, buffer operations" },
  { id: "functions", label: "Functions & Recursion", icon: "🔁", desc: "Call stack, tail recursion, function pointers, variadic args" },
  { id: "structs_unions", label: "Structs & Unions", icon: "📦", desc: "Struct padding, bitfields, tagged unions, nested structs" },
  { id: "memory_management", label: "Dynamic Memory", icon: "🗄️", desc: "malloc/calloc/realloc/free, heap vs stack, fragmentation" },
  { id: "file_io", label: "File I/O", icon: "📁", desc: "fopen/fread/fwrite, binary files, stdin/stdout buffering" },
  { id: "preprocessor", label: "Preprocessor & Macros", icon: "⚙️", desc: "Macro pitfalls, include guards, conditional compilation" },
  { id: "bit_manipulation", label: "Bit Manipulation", icon: "🔢", desc: "Bitwise ops, masks, shifting, packing data" },
  { id: "compilation", label: "Compilation & Linking", icon: "🔗", desc: "gcc flags, object files, extern/static, undefined behavior" },
];

const DSA_TOPICS = [
  { id: "arrays_algo", label: "Array Algorithms", icon: "📊", desc: "Sliding window, two pointer, prefix sum, Kadane's" },
  { id: "linked_list", label: "Linked Lists", icon: "🔗", desc: "Singly/doubly/circular, fast-slow pointers, reversal" },
  { id: "stacks_queues", label: "Stacks & Queues", icon: "🥞", desc: "Monotonic stack, deque, applications in parsing" },
  { id: "trees", label: "Trees & BSTs", icon: "🌳", desc: "DFS/BFS, AVL, segment trees, lowest common ancestor" },
  { id: "graphs", label: "Graphs", icon: "🕸️", desc: "BFS/DFS, Dijkstra, Floyd-Warshall, topological sort" },
  { id: "sorting", label: "Sorting Algorithms", icon: "🔀", desc: "Merge/Quick/Heap sort, counting sort, stability" },
  { id: "dynamic_programming", label: "Dynamic Programming", icon: "🧩", desc: "Memoization, tabulation, knapsack, LCS, matrix chain" },
  { id: "hashing", label: "Hashing", icon: "🔑", desc: "Hash tables in C, collision resolution, hash functions" },
  { id: "recursion_backtracking", label: "Recursion & Backtracking", icon: "🌀", desc: "N-queens, maze solving, permutations, pruning" },
];

const DURATIONS = [
  { value: 10, label: "10 min", desc: "Quick round" },
  { value: 20, label: "20 min", desc: "Standard" },
  { value: 30, label: "30 min", desc: "Deep dive" },
];

export default function TopicSelector({ navigate }) {
  const { candidate, setSession } = useContext(SessionContext);
  const [selectedC, setSelectedC] = useState([]);
  const [selectedDSA, setSelectedDSA] = useState([]);
  const [duration, setDuration] = useState(30);
  const [numQ, setNumQ] = useState(15);
  const [interviewMode, setInterviewMode] = useState("demo_rl");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggleC = (id) => setSelectedC(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);
  const toggleDSA = (id) => setSelectedDSA(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  const totalSelected = selectedC.length + selectedDSA.length;

  const handleStart = async () => {
    if (totalSelected === 0) { setError("Select at least one topic."); return; }
    setLoading(true); setError("");
    try {
      let activeCandidate = candidate;
      if (!activeCandidate?.id) {
        activeCandidate = {
          id: "cand_" + Math.random().toString(36).substring(2, 9),
          name: "Guest Candidate",
          email: "guest@example.com",
        };
        setCandidate(activeCandidate);
      }
      const session = await api.createSession({
        candidate_id: activeCandidate.id,
        c_topics: selectedC,
        dsa_topics: selectedDSA,
        duration_minutes: duration,
        num_questions: interviewMode === "demo_rl" ? 15 : (numQ || 15),
        interview_mode: interviewMode,
      });
      setSession(session);
      navigate("interview");

    } catch (e) {
      setError(e.message || "Could not create session.");
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="topic-page page">
      <Topbar navigate={navigate} showNav={false} />

      <div className="topic-content">
        <div className="topic-hero fade-up">
          <div className="badge badge-accent" style={{ marginBottom: 16 }}>
            Step 2 of 3 — Configure Interview
          </div>
          <h1>Choose your topics</h1>
          <p style={{ color: "var(--text-2)", marginTop: 8, maxWidth: 480 }}>
            Select the C language concepts and DSA topics you want to be tested on.
            The AI will adaptively mix questions based on your performance.
          </p>
        </div>

        <div className="topic-layout">
          {/* Main topic panels */}
          <div className="topic-panels fade-up stagger-1">
            <section className="topic-section">
              <div className="section-header">
                <span className="section-icon">C</span>
                <div>
                  <h3>C Language</h3>
                  <span className="section-count">{selectedC.length} selected</span>
                </div>
              </div>
              <div className="topic-grid">
                {C_TOPICS.map(t => (
                  <TopicCard key={t.id} topic={t}
                    selected={selectedC.includes(t.id)}
                    onClick={() => toggleC(t.id)} />
                ))}
              </div>
            </section>

            <div className="divider" style={{ margin: "32px 0" }} />

            <section className="topic-section">
              <div className="section-header">
                <span className="section-icon" style={{ background: "linear-gradient(135deg, var(--accent-2), #00b8d9)" }}>
                  DSA
                </span>
                <div>
                  <h3>Data Structures & Algorithms</h3>
                  <span className="section-count">{selectedDSA.length} selected</span>
                </div>
              </div>
              <div className="topic-grid">
                {DSA_TOPICS.map(t => (
                  <TopicCard key={t.id} topic={t}
                    selected={selectedDSA.includes(t.id)}
                    onClick={() => toggleDSA(t.id)} />
                ))}
              </div>
            </section>
          </div>

          {/* Config panel */}
          <aside className="config-panel fade-up stagger-2">
            <div className="card" style={{ padding: 24 }}>
              <h3 style={{ marginBottom: 20, fontFamily: "Syne", fontSize: 16 }}>Interview Settings</h3>

              <div style={{ marginBottom: 20 }}>
                <div className="config-label">Duration</div>
                <div className="duration-grid">
                  {DURATIONS.map(d => (
                    <button type="button" key={d.value}
                      className={`duration-btn ${duration === d.value ? "active" : ""}`}
                      onClick={() => setDuration(d.value)}
                    >
                      <strong>{d.label}</strong>
                      <span>{d.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: 24 }}>
                <div className="config-label">
                  Questions: <strong style={{ color: "var(--accent)" }}>{interviewMode === "demo_rl" ? 15 : numQ}</strong>
                </div>
                <input type="range" min={3} max={10} value={numQ}
                  onChange={e => setNumQ(+e.target.value)}
                  className="slider"
                  disabled={interviewMode === "demo_rl"}
                  style={{ width: "100%", accentColor: "var(--accent)" }}
                />
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--text-3)", marginTop: 4 }}>
                  <span>3</span><span>10</span>
                </div>
                {interviewMode === "demo_rl" && (
                  <div style={{ fontSize: 11, color: "var(--text-3)", marginTop: 6 }}>
                    Demo Interview always uses a full 15-question interview mix.
                  </div>
                )}
              </div>

              <div style={{ marginBottom: 24 }}>
                <div className="config-label">Interview mode</div>
                <div style={{ display: "grid", gap: 8 }}>
                  <button
                    type="button"
                    className={`duration-btn ${interviewMode === "standard" ? "active" : ""}`}
                    onClick={() => setInterviewMode("standard")}
                  >
                    <strong>Standard adaptive</strong>
                    <span>Adaptive from the start</span>
                  </button>
                  <button
                    type="button"
                    className={`duration-btn ${interviewMode === "demo_rl" ? "active" : ""}`}
                    onClick={() => setInterviewMode("demo_rl")}
                  >
                    <strong>Demo Interview (15Q)</strong>
                    <span>15-question adaptive interview simulation</span>
                  </button>
                </div>
              </div>

              <div className="divider" />

              <div style={{ fontSize: 13, color: "var(--text-2)", marginBottom: 16 }}>
                <strong>Selected:</strong> {selectedC.length} C + {selectedDSA.length} DSA topics
              </div>

              {totalSelected > 0 && (
                <div style={{ marginBottom: 16 }}>
                  {[...selectedC.map(id => C_TOPICS.find(t => t.id === id)),
                    ...selectedDSA.map(id => DSA_TOPICS.find(t => t.id === id))]
                    .filter(Boolean).map(t => (
                      <span key={t.id} className="badge badge-neutral" style={{ margin: "2px 2px" }}>
                        {t.icon} {t.label}
                      </span>
                    ))}
                </div>
              )}

              {error && <div className="error-banner" style={{ marginBottom: 12 }}>⚠️ {error}</div>}

              <button
                type="button"
                className="btn btn-primary btn-lg"
                style={{ width: "100%", justifyContent: "center", gap: 10 }}
                onClick={handleStart}
                disabled={loading || totalSelected === 0}
              >
                {loading ? <span className="spinner" /> : <>
                  Begin Interview
                  <span style={{ opacity: 0.7, fontSize: 12 }}>→</span>
                </>}
              </button>

              <p style={{ fontSize: 11, color: "var(--text-3)", textAlign: "center", marginTop: 12 }}>
                {interviewMode === "demo_rl"
                  ? "Guided 15-question adaptive interview."
                  : "Interview difficulty starts at your selected level and adapts in real time."}
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

function TopicCard({ topic, selected, onClick }) {
  return (
    <button className={`topic-card ${selected ? "selected" : ""}`} onClick={onClick}>
      <div className="topic-card-header">
        <span className="topic-icon">{topic.icon}</span>
        {selected && <span className="check-mark">✓</span>}
      </div>
      <div className="topic-name">{topic.label}</div>
      <div className="topic-desc">{topic.desc}</div>
    </button>
  );
}
