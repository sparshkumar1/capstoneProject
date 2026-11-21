# Deployment Instructions

Everything in Part A requires your own action (account creation, billing identity, DNS) — nothing here can be done without you. Part B is what you (or I, once you share VM access) run on the provisioned VM.

## Part A — steps only you can do

### A1. Create an Azure for Students account and provision the VM

Switched from Oracle Cloud to Azure for Students because Oracle's standard signup asks for a card (not charged, but still collected) for most users; Azure for Students never asks for or stores a payment method at all. Trade-off: this is a $100/year credit, not a permanent free tier — see `Cost_and_Resource_Analysis.md` for how far that stretches and the stop-the-VM-when-idle strategy to make it last.

1. Go to **azure.microsoft.com/free/students** and sign up with your student email (or redeem it through the GitHub Student Developer Pack if that's the path you have). No card will be requested.
2. In the Azure Portal: **Virtual machines → Create → Azure virtual machine**.
3. Image: **Ubuntu Server 22.04 LTS** (or newer).
4. Size: **Standard_B2ms** (2 vCPU / 8GB RAM — the smaller B2s's 4GB is too tight for this app's backend, which loads torch + sentence-transformers + FAISS + WhisperX + SB3 together). Pick a region close to you to minimize latency.
5. Authentication: SSH public key (generate one locally if you don't have one: `ssh-keygen -t ed25519`) — you'll need this to log in.
6. Disk: the default Standard SSD is fine; no need to oversize it (the Qwen GGUF model is ~1GB, the app's own footprint is small — SQLite and logs won't grow fast for a capstone-scale demo).
7. **Networking tab**: add inbound rules allowing TCP **80** and **443** from any source. Leave SSH (22) restricted to your own IP if the portal offers that, otherwise restrict it after creation via the VM's Network Security Group.
8. Create the VM and note its **public IP address**.
9. **Important for the credit to last**: once created, you can **Stop (deallocate)** the VM from the portal when you're not actively demoing it — Azure does not charge compute time for a deallocated VM, only the small ongoing disk cost. Starting it again takes under a minute. Treat this as "start before a demo, stop after" rather than leaving it running continuously, unless you want the $100 to burn down in under two months of nonstop uptime (`Cost_and_Resource_Analysis.md` has the math).

### A2. Get a public hostname (Let's Encrypt needs a domain, not a bare IP)

- If you already own a domain: create an `A` record pointing a subdomain (e.g. `prepaired.yourdomain.com`) at the VM's public IP.
- If not: register a free subdomain at [duckdns.org](https://www.duckdns.org) (e.g. `prepaired.duckdns.org`) and point it at the VM's public IP.
- Tell me the hostname you chose once it's set up — it goes into `PUBLIC_DOMAIN` in the VM's `.env`.

### A3. Give me VM access (or run Part B yourself)

Either share SSH access to the VM (IP + the private key you generated, via a secure channel — never paste it in chat) so I can run Part B for you, or run Part B's commands yourself and tell me if anything fails.

## Part B — on the VM

```bash
# 1. System deps
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git python3-pip python3-venv
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # log out/in once for this to take effect

# 2. Clone the repo (use your own auth method — PAT, deploy key, etc.)
git clone <your-repo-url> prepaired
cd prepaired

# 3. Download the Qwen GGUF model (~1.06GB) -- scripts/download_qwen_model.py is
#    pure-stdlib (urllib), no pip install needed
python3 scripts/download_qwen_model.py

# 4. Configure secrets -- create .env in the repo root (NOT committed)
cat > .env <<'EOF'
ADMIN_PASSWORD=<choose a real password, not the placeholder>
PUBLIC_DOMAIN=prepaired.duckdns.org   # whatever you set up in A2
EOF
chmod 600 .env

# 5. Build and start the full stack, including the qwen profile
docker compose --env-file .env --profile qwen up -d --build

# 6. Watch logs until healthy
docker compose logs -f backend qwen caddy
```

Caddy will request its Let's Encrypt certificate automatically on first request to `https://<PUBLIC_DOMAIN>` — this requires ports 80/443 to already be reachable from the internet (A1 above) and the DNS record to already resolve (A2 above) before you start the stack, or the first cert request will fail and Caddy will retry.

## Verifying it's actually up

```bash
curl -s https://<PUBLIC_DOMAIN>/api/health          # backend health
curl -s http://127.0.0.1:8001/health                 # qwen, from inside the VM only
docker compose ps                                     # all services should show "running"/"healthy"
```

Then open `https://<PUBLIC_DOMAIN>` in a browser from a machine that is *not* this VM, and run through `Cloud_Testing_Report.md`'s test list — don't mark anything passed until you've actually clicked through it.

## Updating the deployed code later

```bash
cd prepaired
git pull
docker compose --env-file .env --profile qwen up -d --build
```

SQLite data on the mounted volume survives this (it's outside the containers' own filesystem). The Qwen GGUF file does too (bind-mounted read-only from the host, not baked into the image).

## Restarting / stopping

```bash
docker compose --env-file .env --profile qwen restart   # restart everything
docker compose --env-file .env --profile qwen down      # stop everything (volumes, and the host-mounted ./data, persist)
```
