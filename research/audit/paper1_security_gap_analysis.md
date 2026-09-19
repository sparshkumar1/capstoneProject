# Paper 1 Systems & Security Gap Analysis

**Audit Date**: September 19, 2026  
**Auditor**: Senior Systems & Security Research Auditor  
**Target Publication**: Paper 1 (*Trustworthy Adaptive Multimodal Assessment Architecture*, ATIS 2026)  
**Governing Architecture**: `apps/backend/main.py`, `agents/coding_executor/coding_executor.py`, `agents/coding_executor/sandbox_policy.py`, `services/storage/database.py`  
**Status**: **SECURITY GAP AUDIT COMPLETE**

---

## 1. Executive Summary

This security audit scrutinizes the operational boundaries and security invariants of the PREPAIred platform against three critical vectors:
1. **Authentication, Session Tokens & Identity Boundaries**
2. **WebSocket Protocol Invariants & Message Frame Validation**
3. **Container Sandboxing Primitives & Kernel Boundary Realism**

The objective is to replace aspirational claims (e.g., *"100% mathematical containment"*, *"tamper-proof isolation"*) with scientifically defensible, verifiable systems security assertions suitable for peer-reviewed publication.

---

## 2. Authentication, Session Tokens & Tenant Isolation

### 2.1 Current Implementation Reality
- **Session Representation:** Sessions are indexed via UUIDv4 identifiers (`session_id`) stored in memory (`SESSIONS: Dict[str, InterviewOrchestrator]`) and persisted in SQLite (`interview_sessions` table).
- **Session Lookup:** Endpoints (`/api/sessions/{session_id}`, `/api/reports/{session_id}`) query by `session_id`. If found, data is returned; if not, returns HTTP 404.
- **Identified Gap:** The API lacks signed cryptographic session tokens (e.g., HMAC-SHA256 or JWT bearer tokens). A client possessing a valid `session_id` UUID can query and mutate session state without presenting an explicit identity bearer signature.
- **Tenant Isolation Findings:**
  - Database queries (`get_candidate_history`, `get_question_attempts`) correctly scope by `candidate_id` or `session_id`. Cross-candidate queries return disjoint records.
  - In-memory orchestrator instances maintain isolated conversational histories and question queues.
- **Publication Requirement for Paper 1:**
  - Paper 1 must explicitly characterize the current model as **UUIDv4 Unpredictable Capability Tokens** ($\approx 122$ bits of entropy), not a federated OAuth2/JWT cryptosystem.
  - Acknowledge the absence of cryptographic request signing as an engineering roadmap item for multi-tenant enterprise deployment.

---

## 3. WebSocket Validation & Transport Boundary

### 3.1 Implementation Reality (`apps/backend/main.py:1064-1216`)
- **Connection Handshake:** Endpoint `/ws/interview/{session_id}` accepts the WebSocket connection and immediately verifies `session_id in SESSIONS`. Non-existent sessions receive an explicit error frame (`{"type": "error", "payload": {"message": "Session not found"}}`) and the socket is closed immediately.
- **Frame Decoding:** Each incoming text frame is wrapped in a `json.loads(raw)` try-catch block. Malformed non-JSON frames trigger structured error responses (`{"type": "error", "payload": {"message": "Invalid JSON"}}`) without crashing the event loop or disconnecting the candidate.
- **Message Dispatch:** Message types are strictly enumerated (`start`, `voice_answer`, `code_submission`, `next_question`, `request_hint`, `skip_question`, `end_session`). Unknown message types are ignored safely.

### 3.2 Identified Security Gaps
1. **No Handshake Authentication:** The WebSocket handshake does not validate an HTTP Authorization header or signed query token; it relies entirely on the possession of the `session_id`.
2. **Rate Limiting / Flood Protection:** There is no in-process leaky-bucket or token-bucket rate limiter. An adversarial client can emit hundreds of rapid frames per second, causing CPU overhead on the backend JSON parser.
3. **Payload Size Caps:** While the underlying web server (Uvicorn) enforces default HTTP limits, individual WebSocket text frames are not explicitly capped at the application layer.

### 3.3 Publication Framing
- Report WebSocket protocol validation as **Robust Structured Event Dispatching with Exception Trapping**.
- Acknowledge that application-level rate limiting and frame-size clamping represent defense-in-depth enhancements for production environments exposed to public networks.

---

## 4. Container Sandboxing Primitives & Kernel Boundary

### 4.1 Implementation Reality (`agents/coding_executor/coding_executor.py`)
Candidate C code is executed within isolated, ephemeral Docker containers using the following command-line flags:
- `--network=none`: Disables all container network interfaces (loopback only).
- `--read-only`: Makes the container root filesystem strictly read-only.
- `--tmpfs /workspace:rw,noexec,nosuid,size=64m`: In-memory workspace for temporary code and object files.
- `--user 1001:1001`: Non-root user execution.
- `--cap-drop=ALL`: Drops all 41 Linux kernel capabilities.
- `--memory=128m`: Strict memory ceiling via cgroups.
- `--pids-limit=32`: Blocks fork bombs.
- Execution timeout: 2.0s wall-clock SIGKILL.

### 4.2 Gap Between Draft Claims and Security Reality
- **Historical Draft Overclaim:** Earlier drafts claimed *"containerization provides absolute mathematical isolation against host penetration."*
- **Empirical Security Reality:** Docker containers share the host Linux kernel. Containerization provides operating-system level resource isolation (namespaces, cgroups, LSM/seccomp), but is fundamentally **not** hardware virtualization (Type-1/Type-2 hypervisors) or a formally verified microkernel (e.g., seL4).
- **Kernel Attack Surface:** If a candidate exploits an unpatched kernel vulnerability (e.g., dirty pipe, namespace privilege escalation), container breakout is theoretically possible on unhardened hosts.

### 4.3 Defensible Scientific Framing for Paper 1
1. **Downgrade to "Defense-in-Depth OS Containment":** State clearly that PREPAIred employs a 3-tier containment strategy:
   - Tier 1: Static AST and source regex pattern filtering.
   - Tier 2: Compiler diagnostic boundaries and execution timeout caps.
   - Tier 3: Linux cgroups, read-only rootfs, non-root user, and `--cap-drop=ALL`.
2. **Acknowledge Virtualization Trade-offs:** Discuss latency versus isolation trade-offs: Docker container reuse achieves sub-500ms execution latency, whereas full microVM virtualization (e.g., Firecracker / gVisor) provides stronger isolation boundaries at the expense of higher cold-start overhead.
3. **Empirical Negative Tests:** Emphasize that the 9-vector negative security suite (SEC-01 to SEC-09) empirically confirms containment of fork bombs, socket creation, filesystem writes, memory exhaustion, and infinite loops.
