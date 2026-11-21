# Cost and Resource Analysis

## Switched from Oracle to Azure for Students — not "free forever" anymore, but genuinely no-card

Oracle Cloud's Always-Free tier is a permanent $0 VM, but standard signup collects a credit card for identity (not charged unless upgraded). You asked for a path that never asks for card details at all, so this deployment uses **Azure for Students** instead: $100/year credit, renewable annually while enrolled, **no payment method ever attached to the account** — when the credit hits zero, Azure deallocates the VM rather than billing anything, because there's nothing to bill.

## Current cost: $0, bounded by a credit, not a true "forever free" tier

| Component | Where | Cost |
|---|---|---|
| Compute | One Azure `Standard_B2ms` VM (2 vCPU/8GB RAM), Ubuntu 22.04 | ~$0.0832/hr (~$61/mo) while **running**; **$0 while stopped/deallocated** (East US pricing, Sept 2026 — verify current rate in the Azure portal before relying on it) |
| Persistent disk (SQLite + Qwen model) | Azure Managed Disk (Standard SSD, default size) | A few dollars/month regardless of VM running state — draws from the same $100 credit |
| HTTPS certificate | Caddy + Let's Encrypt (automatic) | $0 |
| DNS / public hostname | Free dynamic-DNS subdomain (e.g. DuckDNS) unless you already own a domain | $0 |
| Bandwidth | Azure for Students includes an outbound allowance; demo-scale traffic shouldn't meaningfully dent the $100 credit on its own | ~$0 under normal use |

**The arithmetic that matters:** at ~$61/mo compute, $100 of credit covers under 2 months of continuous uptime, before disk cost. Running the VM only when you're actually demoing/testing (start it, use it, stop/deallocate it — see `Deployment_Instructions.md` A1 step 9) is what makes a $100/year credit stretch across a whole year of occasional use instead of two months of leaving it always-on. This is a real behavioral difference from the original Oracle plan, which assumed the VM could just stay up permanently — flagging it clearly rather than quietly treating the two as equivalent.

## What happens if the credit runs out

- Azure deallocates the VM. No charge is possible — no payment method is on file.
- The managed disk (and the data on it: SQLite DB, Qwen model file) is **not** deleted automatically, but will itself be removed if the subscription is fully disabled after both the credit and the 12-month window expire — back up before that point (see "Backups" below).
- Renewable annually with a fresh $100 while still enrolled as a student — not a one-time allowance.

## Resource footprint (estimated, not yet measured on a live instance — see `Cloud_Testing_Report.md`)

Rough RAM budget inside the 8GB `B2ms`, all services running at once via Docker Compose:
- Backend container (torch + sentence-transformers + faiss + whisperx + SB3, loaded in-process): the single largest consumer — likely several GB once all models are warmed, and the main reason `B2s`'s 4GB was ruled out rather than just picking the cheaper size.
- Qwen container (llama-cpp-python, 1.5B GGUF q4_k_m): small, roughly 1-2GB.
- Frontend (nginx static build) and Caddy: negligible, tens of MB each.
- Evaluator standalone container: present but idle unless called directly (nothing in the live app does) — lazy-loads its models only on first request.

8GB is tighter than the 12GB originally planned for Oracle — worth watching `docker stats` closely on first real run (`Cloud_Testing_Report.md`) and stopping the standalone `evaluator` container (`docker compose stop evaluator`) if memory pressure shows up, since it's not on the critical path anyway.

These are estimates from reading the dependency list, not a measurement — the real numbers belong in `Cloud_Testing_Report.md` once the VM exists. Do not quote these as measured results elsewhere.

## Backups

SQLite lives at `PREPAIRED_DB_PATH` on the VM's persistent disk. Nothing in this migration adds automated off-VM backups — more important here than it would be on a permanent free tier, since this VM has a real (if renewable) expiry condition. A manual step worth doing before relying on this for data you can't afford to lose: periodically `scp` `data/prepaired.db` off the VM, or push it to a cheap/free object-storage tier. Not implemented as part of this pass; flagging it as a gap rather than silently leaving it undocumented.
