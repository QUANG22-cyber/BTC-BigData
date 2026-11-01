import os
from pathlib import Path

import pandas as pd

DATA_ROOT = Path(os.getenv("DATA_ROOT", "data"))
INPUT = DATA_ROOT / "silver" / "futures" / "BTCUSDT" / "klines" / "interval=1m" / "klines.parquet"
OUTPUT_BASE = DATA_ROOT / "gold" / "futures" / "BTCUSDT"


def main():
    if not INPUT.exists():
        print(f"Missing {INPUT}. Run normalize_klines first.")
        return
    df = pd.read_parquet(INPUT)
    if df.empty:
        print("Silver dataset is empty.")
        return
    df = df.set_index("open_time").sort_index()
    agg = {
        "open": "first", "high": "max", "low": "min", "close": "last",
        "volume": "sum", "quote_volume": "sum", "trade_count": "sum",
        "taker_buy_volume": "sum", "taker_buy_quote_volume": "sum",
    }
    expected = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}
    for rule, label in [("15min", "M15"), ("1h", "H1"), ("4h", "H4"), ("1D", "D1")]:
        grouped = df.resample(rule, origin="start_day", label="left", closed="left")
        out = grouped.agg(agg)
        out["candle_count"] = grouped["close"].count()
        out["is_complete_by_count"] = out["candle_count"] == expected[label]
        out = out.dropna(subset=["open", "high", "low", "close"]).reset_index(names="open_time")
        out["timeframe"] = label
        folder = OUTPUT_BASE / f"timeframe={label}"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "candles.parquet"
        out.to_parquet(path, index=False)
        print(f"{label}: {len(out):,} candles -> {path}")


if __name__ == "__main__":
    main()
