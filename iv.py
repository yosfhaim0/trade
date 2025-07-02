from typing import List, Dict
from datetime import datetime
import time
import yfinance as yf
from py_vollib.black_scholes.implied_volatility import implied_volatility

def get_multiple_iv_yahoo(tickers: List[str], delay_between=1.5) -> Dict[str, float]:
    """
    Compute implied volatility (IV) for multiple tickers using Yahoo Finance.

    Returns a dictionary: { "AAPL": 0.3251, "TSLA": 0.4123, ... }
    """
    results = {}

    for ticker in tickers:
        try:
            print(f"🔍 Processing {ticker}...")
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if hist.empty:
                print(f"⚠️ No historical price data for {ticker}")
                continue

            price = hist["Close"].iloc[-1]

            options_dates = stock.options
            if not options_dates:
                print(f"⚠️ No options data for {ticker}")
                continue

            expiry = options_dates[0]
            opt_chain = stock.option_chain(expiry)
            calls = opt_chain.calls
            calls = calls.dropna(subset=["bid", "ask", "strike"])

            # Filter to get the nearest strike
            calls['diff'] = abs(calls['strike'] - price)
            nearest = calls.sort_values('diff').iloc[0]

            strike = nearest['strike']
            bid = nearest['bid']
            ask = nearest['ask']
            mid = (bid + ask) / 2

            if mid <= 0:
                print(f"⚠️ Invalid mid price for {ticker}")
                continue

            t = (datetime.strptime(expiry, "%Y-%m-%d") - datetime.utcnow()).days / 365.0
            if t <= 0:
                print(f"⚠️ Expiry already passed for {ticker}")
                continue

            iv = implied_volatility(
                price=mid,
                S=price,
                K=strike,
                t=t,
                r=0.01,  # risk-free rate assumption
                flag='c'
            )
            results[ticker] = round(iv, 4)

        except Exception as e:
            print(f"❌ Error with {ticker}: {e}")
        finally:
            time.sleep(delay_between)

    return results


if __name__ == '__main__':
    tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOG', 'AMD', 'NVDA', 'INTC']
    iv_results = get_multiple_iv_yahoo(tickers)
    print("\n📈 Implied Volatility (Yahoo Finance):")
    for t, iv in iv_results.items():
        print(f"{t}: IV = {iv}")
