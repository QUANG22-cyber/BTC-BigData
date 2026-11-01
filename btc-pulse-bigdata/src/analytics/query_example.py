import os
from pathlib import Path

import duckdb

DATA_ROOT = Path(os.getenv("DATA_ROOT", "data"))
PARQUET = DATA_ROOT / "silver" / "futures" / "BTCUSDT" / "klines" / "interval=1m" / "klines.parquet"


def main():
    if not PARQUET.exists():
        print(f"Missing {PARQUET}. Run historical_loader and normalize_klines first.")
        return
    con = duckdb.connect()
    query = '''
        SELECT COUNT(*) AS candle_count,
               MIN(open_time) AS first_candle_utc,
               MAX(open_time) AS last_candle_utc,
               MIN(close) AS min_close,
               MAX(close) AS max_close,
               AVG(volume) AS avg_base_volume
        FROM read_parquet(?)
    '''
    print(con.execute(query, [str(PARQUET)]).df().to_string(index=False))


if __name__ == "__main__":
    main()
