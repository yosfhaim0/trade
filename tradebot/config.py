import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ExchangeConfig:
    api_key: str
    api_secret: str
    sandbox: bool = False
    default_type: str = "spot"


@dataclass(frozen=True)
class StrategyConfig:
    name: str = "swing"
    symbol: str = "BTC/USDT"
    timeframe: str = "1d"
    short_ema: int = 5
    long_ema: int = 20
    risk_fraction: float = 0.1


@dataclass(frozen=True)
class BotConfig:
    exchange: ExchangeConfig
    strategy: StrategyConfig
    poll_interval_seconds: int = 3600
    reports_dir: Path = Path("reports")


DEFAULTS: Dict[str, Any] = {
    "sandbox": False,
    "default_type": "spot",
    "strategy": "swing",
    "symbol": "BTC/USDT",
    "timeframe": "1d",
    "short_ema": 5,
    "long_ema": 20,
    "risk_fraction": 0.1,
    "poll_interval_seconds": 3600,
}


def load_config(path: Path) -> BotConfig:
    data = json.loads(path.read_text())
    exchange = ExchangeConfig(
        api_key=data["api_key"],
        api_secret=data["api_secret"],
        sandbox=data.get("sandbox", DEFAULTS["sandbox"]),
        default_type=data.get("default_type", DEFAULTS["default_type"]),
    )
    strategy = StrategyConfig(
        name=data.get("strategy", DEFAULTS["strategy"]),
        symbol=data.get("symbol", DEFAULTS["symbol"]),
        timeframe=data.get("timeframe", DEFAULTS["timeframe"]),
        short_ema=int(data.get("short_ema", DEFAULTS["short_ema"])),
        long_ema=int(data.get("long_ema", DEFAULTS["long_ema"])),
        risk_fraction=float(data.get("risk_fraction", DEFAULTS["risk_fraction"])),
    )
    poll_interval = int(
        data.get("poll_interval_seconds", DEFAULTS["poll_interval_seconds"])
    )
    reports_dir = Path(data.get("reports_dir", "reports"))
    return BotConfig(
        exchange=exchange,
        strategy=strategy,
        poll_interval_seconds=poll_interval,
        reports_dir=reports_dir,
    )
