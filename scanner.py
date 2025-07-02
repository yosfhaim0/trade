from typing import List, Dict
import pandas as pd

from data_collector import DataCollector
from database import Database
from analyzer import Analyzer


class Scanner:
    """Run scans on stocks using technical indicators."""

    def __init__(self, db_path: str = "market.db"):
        self.collector = DataCollector()
        self.db = Database(db_path)
        self.analyzer = Analyzer()

    def update_data(self, tickers: List[str]):
        for ticker in tickers:
            df = self.collector.fetch_historical(ticker, period="60d", interval="1d")
            if df.empty:
                continue
            self.db.insert_dataframe(ticker, df)

    def scan(self, tickers: List[str]) -> pd.DataFrame:
        rows = []
        for ticker in tickers:
            df = self.db.fetch_dataframe(ticker, limit=60)
            if df.empty:
                continue
            df = self.analyzer.add_indicators(df)
            support, resistance = self.analyzer.support_resistance(df)
            latest = df.iloc[-1]
            close = latest["Close"]
            rsi = latest["RSI"]
            near_support = any(abs(close - level) / close < 0.01 for level in support)
            near_resistance = any(abs(close - level) / close < 0.01 for level in resistance)
            if rsi > 70 or rsi < 30 or near_support or near_resistance:
                rows.append({
                    "Ticker": ticker,
                    "Close": round(close, 2),
                    "RSI": round(rsi, 2),
                    "NearSupport": near_support,
                    "NearResistance": near_resistance,
                })
        return pd.DataFrame(rows)


def main():
    tickers = ["AAPL", "MSFT", "GOOG"]
    scanner = Scanner()
    scanner.update_data(tickers)
    result = scanner.scan(tickers)
    if not result.empty:
        print(result.to_string(index=False))
    else:
        print("No signals found")


if __name__ == "__main__":
    main()
