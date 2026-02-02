from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from tradebot.config import StrategyConfig
from tradebot.exchange import Balance


@dataclass
class Signal:
    action: str
    reason: str


class Strategy:
    def generate_signal(
        self, prices: List[float], balances: dict[str, Balance]
    ) -> Optional[Signal]:
        raise NotImplementedError


class SwingStrategy(Strategy):
    def __init__(self, config: StrategyConfig) -> None:
        self._config = config

    def generate_signal(
        self, prices: List[float], balances: dict[str, Balance]
    ) -> Optional[Signal]:
        if len(prices) < self._config.long_ema + 1:
            return None
        short_ema = _ema(prices, self._config.short_ema)
        long_ema = _ema(prices, self._config.long_ema)
        base_asset, _ = self._config.symbol.split("/")
        base_balance = balances.get(base_asset, Balance(0.0, 0.0))
        has_position = base_balance.free > 0
        if short_ema > long_ema and not has_position:
            return Signal(action="buy", reason="short EMA above long EMA")
        if short_ema < long_ema and has_position:
            return Signal(action="sell", reason="short EMA below long EMA")
        return None


def _ema(prices: List[float], window: int) -> float:
    multiplier = 2 / (window + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema
