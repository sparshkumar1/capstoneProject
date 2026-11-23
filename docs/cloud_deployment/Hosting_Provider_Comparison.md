# Hosting Provider Comparison

Researched live via web search on 2026-11-15 (not from memory — free-tier terms change often). Constraint driving this: **must stay $0/month** and **SQLite needs a real persistent disk**, not an ephemeral container filesystem.

| Platform | Free compute | Free persistent disk | Verdict | Source |
|---|---|---|---|---|
| Render | Yes (sleeps on idle) | **No** — free web services cannot attach a disk at all; filesystem resets on every restart/redeploy/sleep. Disk is $0.25/GB and only works on the paid $7/mo+ tier. | Fails the persistence requirement at $0. | [actualdatabase.com](https://actualdatabase.com/render-free-vs-starter-pricing/) |
| Fly.io | **No free tier for new accounts** since Oct 7, 2024 — only a 2 VM-hour / 7-day trial. Legacy accounts on deprecated plans keep a small allowance. | Volumes billed at $0.15/GB/mo regardless, even when unattached. | Fails at $0 for a new account. | [budgetforge.dev](https://www.budgetforge.dev/tools/fly-io-pricing-2026-2) |
| Railway | "Free" plan is $1/mo in non-rollover credit after a one-time $5/30-day trial — not enough to run a service continuously. | N/A (compute itself isn't sustainably free) | Fails at $0. | [saaspricepulse.com](https://www.saaspricepulse.com/tools/railway) |
| Hugging Face Spaces | Free CPU basic: 2 vCPU / 16GB RAM / 50GB disk. | Disk is **ephemeral** — resets on restart/pause. The `/data` persistent mount is a paid upgrade ($5–100/mo by size). Some recent reports say new free Docker/CPU Spaces may now require a $9 PRO account — unconfirmed/conflicting at time of writing, worth re-checking before relying on it. | Fails the persistence requirement at $0; good option if you later accept ephemeral SQLite + external backup. | [altftool.com](https://www.altftool.com/lookouts/free-domain-hosting/cloud/hugging-face-spaces) |
| **Oracle Cloud "Always Free"** | 2 OCPU / 12GB RAM Ampere A1 (down from 4/24 earlier in 2026), indefinite, no trial expiry. | **Yes** — real block storage allowance, persists as long as the instance isn't idle-reclaimed (Oracle monitors CPU/network/memory over rolling 7-day windows and can reclaim instances under ~20% utilization on all three). | **Only option satisfying both constraints at $0.** Costs more setup effort: you run Docker + a reverse proxy yourself instead of a PaaS "deploy" button. Requires card verification at signup for identity (does not itself charge if you stay within Always-Free-labeled shapes). | [terminalbytes.com](https://terminalbytes.com/oracle-cloud-free-tier-changes-2026/) |
| Vercel (frontend-only use) | Static hosting free (Hobby): 100GB bandwidth/mo, 6000 build-min/mo. | N/A — static only | **Hobby tier is explicitly non-commercial-use only** — fine for a research capstone demo, but worth knowing. Not needed here since the frontend is served from the same Azure VM via Caddy. | [justinmckelvey.com](https://justinmckelvey.com/blog/vercel-vs-netlify) |
| Netlify (frontend-only use) | Static hosting free: 100GB bandwidth/mo, 300 build-min/mo, 300 monthly "credits" hard cap. | N/A — static only | Explicitly allows commercial use, unlike Vercel Hobby. Not needed here for the same reason. | [justinmckelvey.com](https://justinmckelvey.com/blog/vercel-vs-netlify) |

## Decision — revised: Azure for Students, not Oracle

Oracle Always-Free was the initial pick (table above), but its standard signup collects a credit card for identity verification even though it isn't charged — ruled out per your explicit "no card details" requirement. There's a no-card Oracle path for "recognized users" (Oracle Academy students, CloudWorld attendees), but eligibility couldn't be confirmed without attempting signup.

Instead: **Azure for Students** (azure.microsoft.com/free/students), confirmed via search to never request or store a payment method on the account. $100/year credit, renewable annually while enrolled; the subscription is deallocated (not billed) when the credit runs out, since there's no card on file to bill.

| | Oracle Always Free (original pick) | Azure for Students (actual pick) |
|---|---|---|
| Card required | Yes, for most users | **No, never** |
| Cost model | Permanent $0, no expiry | $100/year credit, renews while enrolled |
| Compute | 2 OCPU / 12GB RAM, Always Free | `Standard_B2ms`, 2 vCPU / 8GB RAM — picked over the cheaper 4GB `B2s` because this app's backend loads torch + sentence-transformers + FAISS + WhisperX + SB3 together |
| Sustaining it long-term | Just leave it running | Stop/deallocate the VM when not actively demoing — compute isn't billed while stopped, only small disk cost continues (see `Cost_and_Resource_Analysis.md`) |

Single `Standard_B2ms` Ubuntu VM running the whole Docker Compose stack (backend + evaluator + qwen + frontend + Caddy), per `Cloud_Architecture.md`.

## Known risk with this choice

Unlike the Oracle plan, this VM has a real (if annually-renewable) expiry condition tied to the credit balance, not an idle-reclamation policy. The operational habit that matters here is different: start the VM before you need it, stop it after, and keep an eye on the remaining credit in the Azure portal so you're not surprised by a sudden deallocation mid-use.
