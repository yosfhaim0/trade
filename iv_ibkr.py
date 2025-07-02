from ib_insync import IB, Stock
import pandas as pd
from datetime import datetime

def get_iv_rank_ibkr(tickers, ib: IB):
    iv_data = {}
    for t in tickers:
        try:
            print(f"🔍 Getting IV data for {t}")
            con = Stock(t, 'SMART', 'USD')
            ib.qualifyContracts(con)
            hist = ib.reqHistoricalVolatility(con, '', '', '1 Y', '1 day', False)
            ivs = [x.impliedVolatility for x in hist if x.impliedVolatility is not None]
            if not ivs:
                print(f"⚠️ No IV data for {t}")
                continue
            current = ivs[-1]
            iv_low, iv_high = min(ivs), max(ivs)
            rank = (current - iv_low) / (iv_high - iv_low) if iv_high != iv_low else 0
            iv_data[t] = {'iv': current, 'low': iv_low, 'high': iv_high, 'rank': round(rank, 4)}
        except Exception as e:
            print(f"❌ Error fetching {t}: {e}")
    return iv_data

if __name__ == '__main__':
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=2)
    tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOG', 'AMZN']
    results = get_iv_rank_ibkr(tickers, ib)

    print("\n📊 52-Week IV Rank:")
    for t, d in results.items():
        print(f"{t}: IV={d['iv']:.4f}, Low={d['low']:.4f}, High={d['high']:.4f}, Rank={d['rank']*100:.1f}%")

    ib.disconnect()
