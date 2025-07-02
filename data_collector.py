import yfinance as yf
import pandas as pd

class DataCollector:
    """Fetches historical and current stock data using yfinance."""

    def fetch_historical(self, ticker: str, period: str = "30d", interval: str = "1d") -> pd.DataFrame:
        """Return historical OHLCV data for a ticker."""
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.dropna(how="any", inplace=True)
        return df

    def fetch_current(self, tickers):
        """Fetch the most recent price and volume for one or multiple tickers."""
        if isinstance(tickers, str):
            tickers = [tickers]
        df = yf.download(tickers, period="1d", interval="1m", progress=False)
        latest = {}
        if isinstance(df.columns, pd.MultiIndex):
            for t in tickers:
                try:
                    series = df[t].iloc[-1]
                    latest[t] = {
                        "price": float(series["Close"]),
                        "volume": int(series["Volume"]),
                    }
                except Exception:
                    continue
        else:
            series = df.iloc[-1]
            latest[tickers[0]] = {
                "price": float(series["Close"]),
                "volume": int(series["Volume"]),
            }
        return latest
