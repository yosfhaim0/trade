from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol

import ccxt

from tradebot.config import ExchangeConfig


@dataclass
class Balance:
    free: float
    locked: float


@dataclass
class OrderResult:
    id: str
    status: str
    side: str
    price: float
    amount: float


class ExchangeClient(Protocol):
    def fetch_balances(self) -> Dict[str, Balance]:
        ...

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> List[List[float]]:
        ...

    def fetch_open_orders(self, symbol: str) -> List[dict]:
        ...

    def create_market_order(self, symbol: str, side: str, amount: float) -> OrderResult:
        ...


class CCXTBinanceClient:
    def __init__(self, config: ExchangeConfig) -> None:
        self._exchange = ccxt.binance(
            {
                "apiKey": config.api_key,
                "secret": config.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": config.default_type},
            }
        )
        self._exchange.set_sandbox_mode(config.sandbox)

    def fetch_balances(self) -> Dict[str, Balance]:
        account = self._exchange.private_get_account()
        balances: Dict[str, Balance] = {}
        for entry in account["balances"]:
            free = float(entry["free"])
            locked = float(entry["locked"])
            balances[entry["asset"]] = Balance(free=free, locked=locked)
        return balances

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> List[List[float]]:
        return self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def fetch_open_orders(self, symbol: str) -> List[dict]:
        return self._exchange.fetch_open_orders(symbol)

    def create_market_order(self, symbol: str, side: str, amount: float) -> OrderResult:
        order = self._exchange.create_order(symbol, "market", side, amount)
        return OrderResult(
            id=str(order["id"]),
            status=str(order["status"]),
            side=str(order["side"]),
            price=float(order.get("price") or 0.0),
            amount=float(order.get("amount") or amount),
        )
