import argparse
from pathlib import Path

from tradebot.config import load_config
from tradebot.exchange import CCXTBinanceClient
from tradebot.trader import TradeBot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crypto trading bot")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config_paper.json"),
        help="Path to config file",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle instead of looping",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    exchange = CCXTBinanceClient(config.exchange)
    bot = TradeBot(config, exchange)
    if args.once:
        bot.run_once()
    else:
        bot.run_forever()


if __name__ == "__main__":
    main()
