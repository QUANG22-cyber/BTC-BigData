# Stage 2 — Periodic ingestion

Owner: member 2.

Responsibilities:
- Schedule historical loads and regular integrity checks.
- Track the latest verified candle and ingestion-run status.
- Detect gaps and trigger REST API backfill.
- Record start/end times, counts, failures, and retries.

Milestone 1: run the historical loader manually. Milestone 2: add Cron or Airflow after schema and checkpoint rules are agreed with members 1 and 3. Do not claim automated gap recovery until gap detection and idempotent writes are implemented and tested.
