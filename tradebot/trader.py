from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from tradebot.config import BotConfig
from tradebot.exchange import Balance, ExchangeClient
from tradebot.reporter import BotStatus, Reporter
from tradebot.strategy import Signal, SwingStrategy


@dataclass
class MarketSnapshot:
    closes: List[float]
    last_price: float


class TradeBot:
    def __init__(self, config: BotConfig, exchange: ExchangeClient) -> None:
        self._config = config
        self._exchange = exchange
        self._reporter = Reporter(config.reports_dir)
        self._strategy = SwingStrategy(config.strategy)

    def run_forever(self) -> None:
        while True:
            self.run_once()
            time.sleep(self._config.poll_interval_seconds)

    def run_once(self) -> None:
        snapshot = self._fetch_market_data()
        balances = self._exchange.fetch_balances()
        signal = self._strategy.generate_signal(snapshot.closes, balances)
        status = BotStatus(
            symbol=self._config.strategy.symbol,
            signal=signal.action if signal else None,
            reason=signal.reason if signal else None,
            last_price=snapshot.last_price,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._reporter.write_status(status)
        if signal:
            self._execute_signal(signal, balances, snapshot.last_price)

    def _fetch_market_data(self) -> MarketSnapshot:
        limit = max(self._config.strategy.long_ema * 3, 50)
        ohlcv = self._exchange.fetch_ohlcv(
            self._config.strategy.symbol,
            timeframe=self._config.strategy.timeframe,
            limit=limit,
        )
        closes = [entry[4] for entry in ohlcv]
        return MarketSnapshot(closes=closes, last_price=closes[-1])

    def _execute_signal(
        self, signal: Signal, balances: dict[str, Balance], last_price: float
    ) -> None:
        base_asset, quote_asset = self._config.strategy.symbol.split("/")
        if signal.action == "buy":
            quote_balance = balances.get(quote_asset, Balance(0.0, 0.0)).free
            budget = quote_balance * self._config.strategy.risk_fraction
            if budget <= 0:
                return
            amount = budget / last_price
            order = self._exchange.create_market_order(
                self._config.strategy.symbol, "buy", amount
            )
            self._reporter.record_trade(self._config.strategy.symbol, order)
            return
        if signal.action == "sell":
            base_balance = balances.get(base_asset, Balance(0.0, 0.0)).free
            if base_balance <= 0:
                return
            order = self._exchange.create_market_order(
                self._config.strategy.symbol, "sell", base_balance
            )
            self._reporter.record_trade(self._config.strategy.symbol, order)
