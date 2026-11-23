# Database Migration

**Not applicable for this deployment** — per your explicit decision, SQLite is kept as-is, backed by a real persistent volume on the Azure VM instead of migrating to Postgres.

## Why this is safe at this scale

- The single-VM architecture runs exactly one backend process (`--workers 1` in `docker-compose.yml`), matching SQLite's single-writer concurrency model (WAL mode + the app's own `threading.Lock()` in `services/storage/database.py`).
- This is a research-capstone demo, not a multi-replica production service — SQLite's limits (no safe concurrent writers across multiple processes/containers) don't bind unless the backend is scaled horizontally.

## What would force a real migration later

- Running more than one backend replica (SQLite would need to become Postgres/MySQL first — not optional at that point).
- Needing managed backups/point-in-time recovery beyond a manual copy of the `.db` file.

## If it's needed later

Do not start a schema migration without first reading `services/storage/database.py`'s actual schema (`candidates`, `sessions`, `question_attempts`, `bookmarks`, `study_goals` — see `Cloud_Architecture.md`'s source inspection notes) and getting explicit approval, per this project's CLAUDE.md rule on major architecture changes. Not attempted as part of this migration.
