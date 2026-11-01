import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

BASE_URL = os.getenv("BINANCE_REST_BASE", "https://fapi.binance.com")
SYMBOL = os.getenv("BINANCE_SYMBOL", "BTCUSDT")
DATA_ROOT = Path(os.getenv("DATA_ROOT", "data"))
ENDPOINT = f"{BASE_URL}/fapi/v1/klines"


def fetch_klines(start_ms, end_ms):
    rows, cursor = [], start_ms
    while cursor < end_ms:
        response = requests.get(
            ENDPOINT,
            params={"symbol": SYMBOL, "interval": "1m", "startTime": cursor,
                    "endTime": end_ms, "limit": 1000},
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        rows.extend(batch)
        next_cursor = int(batch[-1][0]) + 60_000
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        time.sleep(0.15)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=1)
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days must be >= 1")

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = now - timedelta(days=args.days)
    rows = fetch_klines(int(start.timestamp() * 1000), int(now.timestamp() * 1000))

    folder = DATA_ROOT / "bronze" / "rest_klines" / f"symbol={SYMBOL}" / f"date={now:%Y-%m-%d}"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"klines_{now:%H%M%S}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            record = {
                "source": "binance_um_futures_rest", "market": "um_futures",
                "symbol": SYMBOL, "interval": "1m",
                "open_time_ms": int(row[0]), "open": row[1], "high": row[2],
                "low": row[3], "close": row[4], "volume": row[5],
                "close_time_ms": int(row[6]), "quote_volume": row[7],
                "trade_count": int(row[8]), "taker_buy_volume": row[9],
                "taker_buy_quote_volume": row[10], "ingest_time": now.isoformat(),
            }
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
    print(f"Fetched {len(rows):,} klines -> {path}")


if __name__ == "__main__":
    main()
