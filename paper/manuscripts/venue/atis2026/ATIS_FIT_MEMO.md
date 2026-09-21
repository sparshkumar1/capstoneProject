# ATIS 2026 — fallback fit memo for Paper 1 (not ported; nothing submitted)

ATIS 2026 = 16th International Conference on **Applications and Techniques in Information Security**, 14–15 Dec 2026, Bengaluru, India (site statement).

## Current facts (re-fetched 2026-09-21 from atis2026.com/call-for-papers)
| Item | Finding | Status |
|---|---|---|
| Submission deadline | **7 Nov 2026** | VERIFIED |
| Notification | 30 Nov 2026 | VERIFIED |
| Page limit | "up to 12 pages" | VERIFIED |
| Format | Springer CCIS; LaTeX and Word templates | VERIFIED |
| Review | "three reviewers and one meta-reviewer", with conflict-of-interest filtering. Double-blind was recorded in the earlier pass of 2026-09-21; the re-fetch did not repeat it | double-blind: confirm before submission (treat as anonymous) |
| Indexing | Springer CCIS; "indexed in the Scopus database" | conference claim; not independently confirmed |
| Scope | four tracks covering 40 areas, including secure communications, hardware security, AI/cybersecurity, quantum/cryptography | VERIFIED (summary) |
| Registration fee; AI-use policy | not on the page | UNVERIFIED |

## Fit
Topic fit is moderate to good (containment, prompt-injection-adjacent authority separation, failure handling). Reviewers in an information-security venue will expect a threat model, adversary capabilities and stronger attacks. The paper's scope (fixed programs, one environment, no adaptive attacker) is stated but will be judged against those expectations. This is a stated fit risk, not a prediction.

## Required reframing (no scientific change)
1. Lead with the security-relevant property question, but keep "scoped empirical evidence" and the non-claims (not a security evaluation, no adversary-capability claim).
2. Expand the threat-model paragraph into a short subsection: attacker goals per program (host write, egress, resource exhaustion, process inspection), capabilities (fixed C source), exclusions (adaptive, kernel/runtime exploits, UDP/DNS/IPv6, other platforms).
3. Give the ptrace finding more room: it is the most security-relevant honest result (the application-level filter, not a kernel-level control, carried the outcome; the bypassed call returned 0 in the container).
4. Restore material cut for the six-page ICETC version: the host-observable details per attack, the SEC-08/SEC-09 oracle caveats, and the X1-A table rows.
5. Relate more explicitly to sandbox-benchmark work ([1]–[7]); no additional reference is added in this pass.
6. Keep the same-agent and AI-tool disclosures; Springer's AI policy (not read) will apply.

## Length
The v2 body is about 3,600 words; in CCIS format (12-page limit) it is expected to occupy about 8–10 pages with the restored material (estimate).
