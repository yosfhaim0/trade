from ib_insync import *
from typing import List, Dict
import time

def get_multiple_iv_ibkr(tickers: List[str], ib: IB, delay_between=1.5) -> Dict[str, float]:
    """
    Compute implied volatility (IV) for multiple tickers using IBKR.

    Returns a dictionary: { "AAPL": 0.3251, "TSLA": 0.4123, ... }
    """
    results = {}

    for ticker in tickers:
        try:
            print(f"🔍 Processing {ticker}...")
            stock = Stock(ticker, 'SMART', 'USD')
            ib.qualifyContracts(stock)

            price_data = ib.reqMktData(stock, '', False, False)
            ib.sleep(1.5)
            price = float(price_data.last or price_data.close)
            ib.cancelMktData(stock)

            chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            chain = next((c for c in chains if c.strikes), None)
            if not chain:
                print(f"⚠️ No option chains with strikes for {ticker}")
                continue

            strikes = [s for s in chain.strikes if abs(s - price) < 10]
            if not strikes:
                print(f"⚠️ No nearby strikes for {ticker}")
                continue

            nearest_strike = sorted(strikes, key=lambda s: abs(s - price))[0]
            expiry = sorted(chain.expirations)[0]

            option = Option(ticker, expiry, nearest_strike, 'C', 'SMART')
            ib.qualifyContracts(option)

            option_data = ib.reqMktData(option, '', False, False)

            for _ in range(5):
                ib.sleep(1)
                if option_data.modelGreeks and option_data.modelGreeks.impliedVol:
                    break

            ib.cancelMktData(option)
            iv = option_data.modelGreeks.impliedVol if option_data.modelGreeks else None
            if iv:
                results[ticker] = round(iv, 4)
            else:
                print(f"⚠️ No IV found for {ticker}")

        except Exception as e:
            print(f"❌ Error with {ticker}: {e}")
        finally:
            time.sleep(delay_between)

    return results
if __name__ == '__main__':
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=2)

    tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOG', 'AMD', 'NVDA', 'INTC']
    iv_results = get_multiple_iv_ibkr(tickers, ib)
    print("\n📈 Implied Volatility:")
    for t, iv in iv_results.items():
        print(f"{t}: IV = {iv}")

    ib.disconnect()