import json
import os
from pathlib import Path

import pandas as pd

DATA_ROOT = Path(os.getenv("DATA_ROOT", "data"))
INPUT_ROOT = DATA_ROOT / "bronze" / "rest_klines"
OUTPUT_ROOT = DATA_ROOT / "silver" / "futures" / "BTCUSDT" / "klines" / "interval=1m"


def main():
    files = sorted(INPUT_ROOT.rglob("*.jsonl")) if INPUT_ROOT.exists() else []
    if not files:
        print(f"No REST JSONL files found under {INPUT_ROOT}. Run historical_loader first.")
        return

    records = []
    for path in files:
        with path.open(encoding="utf-8") as f:
            records.extend(json.loads(line) for line in f if line.strip())
    if not records:
        print("No records found.")
        return

    df = pd.DataFrame(records)
    for col in ["open", "high", "low", "close", "volume", "quote_volume",
                "taker_buy_volume", "taker_buy_quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time_ms"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time_ms"], unit="ms", utc=True)
    df["ingest_time_dt"] = pd.to_datetime(df["ingest_time"], utc=True)

    ingest_ms = df["ingest_time_dt"].astype("int64") // 1_000_000

    df = df[df["close_time_ms"] < ingest_ms].copy()
    df = df.drop(columns=["ingest_time_dt"])
    df = df.dropna(subset=["open_time", "open", "high", "low", "close", "volume"])
    df = df.drop_duplicates(subset=["market", "symbol", "interval", "open_time_ms"], keep="last")
    df = df.sort_values("open_time")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_ROOT / "klines.parquet"
    df.to_parquet(out, index=False)
    print(f"Normalized {len(df):,} unique candles -> {out}")


if __name__ == "__main__":
    main()
