import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import websockets

SYMBOL = os.getenv("BINANCE_SYMBOL", "BTCUSDT").lower()
WS_BASE = os.getenv(
    "BINANCE_WS_BASE",
    "wss://fstream.binance.com/market/ws",
)
DATA_ROOT = Path(os.getenv("DATA_ROOT", "data"))
STREAM = f"{SYMBOL}@kline_1m"


def output_file():
    now = datetime.now(timezone.utc)
    folder = DATA_ROOT / "bronze" / "websocket_klines" / f"symbol={SYMBOL.upper()}" / f"date={now:%Y-%m-%d}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"events_{now:%H}.jsonl"


async def run():
    delay = 1
    while True:
        try:
            url = f"{WS_BASE}/{STREAM}"
            print(f"Connecting to {url}")
            async with websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=20,
                max_queue=1000,
            ) as ws:
                print("WebSocket connected successfully. Waiting for events...")
                delay = 1
                async for message in ws:
                    received_at = datetime.now(timezone.utc).isoformat()
                    payload = json.loads(message)
                    record = {
                        "source": "binance_um_futures_websocket",
                        "market": "um_futures", "symbol": SYMBOL.upper(),
                        "stream": STREAM, "event_time_ms": payload.get("E"),
                        "ingest_time": received_at, "payload": payload,
                    }
                    with output_file().open("a", encoding="utf-8") as f:
                        f.write(json.dumps(record, separators=(",", ":")) + "\n")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"WebSocket error: {exc!r}; reconnecting in {delay}s")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Collector stopped.")
