# Stage 3 — Storage contract

- Bronze: raw JSONL from REST/WebSocket.
- Silver: normalized, typed Parquet.
- Gold: derived analytical datasets.
- Metadata: checkpoints, ingestion runs, and quality checks.

All timestamps are UTC. Logical candle key: `(market, symbol, interval, open_time_ms)`.
Do not commit real datasets or database files to Git.
