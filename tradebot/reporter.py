from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tradebot.exchange import OrderResult


@dataclass
class BotStatus:
    symbol: str
    signal: Optional[str]
    reason: Optional[str]
    last_price: float
    timestamp: str


class Reporter:
    def __init__(self, reports_dir: Path) -> None:
        self._reports_dir = reports_dir
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        self._status_path = self._reports_dir / "status.json"
        self._trades_path = self._reports_dir / "trades.csv"

    def write_status(self, status: BotStatus) -> None:
        self._status_path.write_text(json.dumps(asdict(status), indent=2))

    def record_trade(self, symbol: str, order: OrderResult) -> None:
        new_file = not self._trades_path.exists()
        with self._trades_path.open("a", newline="") as handle:
            writer = csv.writer(handle)
            if new_file:
                writer.writerow([
                    "timestamp",
                    "symbol",
                    "order_id",
                    "side",
                    "price",
                    "amount",
                    "status",
                ])
            writer.writerow(
                [
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    order.id,
                    order.side,
                    f"{order.price:.8f}",
                    f"{order.amount:.8f}",
                    order.status,
                ]
            )
