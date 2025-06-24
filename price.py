
import yfinance as yf
import pandas as pd
from time import sleep
from typing import List, Dict



def filter_stocks_by_price(tickers: List[str], min_price=None, max_price=None) -> Dict[str, float]:
    """
    Legacy version — fetches price per ticker one-by-one (slow, subject to rate-limiting)
    """
    result = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            price = stock.info.get("regularMarketPrice", None)
            if price is None:
                continue
            if (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
                result[ticker] = price
        except Exception as e:
            print(f"Error with {ticker}: {e}")
    return result


def batch_filter_stocks_by_price_volume(
    tickers: List[str],
    min_price: float = None,
    max_price: float = None,
    min_volume: int = None,
    batch_size: int = 200
) -> Dict[str, Dict[str, float]]:
    """
    Fast version — fetches price & volume data in batches using yf.download()

    Returns a dictionary:
        {
            "AAPL": {"price": 176.3, "volume": 158000000},
            ...
        }
    """
    filtered = {}

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"🔄 Downloading batch {i // batch_size + 1}: {batch[:3]}... ({len(batch)} tickers)")
        try:
            df = yf.download(batch, period="1d", progress=False, group_by="ticker", threads=True)

            if isinstance(df.columns, pd.MultiIndex):
                for ticker in batch:
                    try:
                        price = df[ticker]['Close'].iloc[-1]
                        volume = df[ticker]['Volume'].iloc[-1]

                        if price is None or volume is None:
                            continue

                        if (min_price is None or price >= min_price) and \
                           (max_price is None or price <= max_price) and \
                           (min_volume is None or volume >= min_volume):
                            filtered[ticker] = {"price": price, "volume": volume}
                    except Exception as e:
                        print(f"❌ Error for {ticker}: {e}")
            else:
                price = df['Close'].iloc[-1]
                volume = df['Volume'].iloc[-1]
                ticker = batch[0]
                if (min_price is None or price >= min_price) and \
                   (max_price is None or price <= max_price) and \
                   (min_volume is None or volume >= min_volume):
                    filtered[ticker] = {"price": price, "volume": volume}

        except Exception as e:
            print(f"⚠️ Batch error: {e}")
            sleep(2)

        sleep(1)

    return filtered
if __name__ == '__main__':
    filtered = batch_filter_stocks_by_price_volume(
        tickers=['AAPL', 'TSLA', 'MSFT'],
        min_price=100,
        max_price=1000,
        min_volume=10_000_000
    )
    print(filtered)