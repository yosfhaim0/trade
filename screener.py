from ib_insync import IB
from price import batch_filter_stocks_by_price_volume
from iv import get_multiple_iv_ibkr
from stochastic import get_stochastic_signals
from support_resistance import get_support_resistance
from ib_insync import IB
import pandas as pd
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)



def get_filtered_stocks(tickers, ib: IB, price_min=20, price_max=800):
    print(f"\n🔍 Start filtering {len(tickers)} tickers...")

    # שלב 1: מחיר
    print("\n📊 Step 1: Filtering by price...")
    price_filtered = batch_filter_stocks_by_price_volume(tickers, min_price=price_min, max_price=price_max)
    if not price_filtered:
        print("❌ No tickers passed price filter.")
        return pd.DataFrame()

    # שלב 2: IV
    print("\n📊 Step 2: Fetching Implied Volatility (IV)...")
    iv_data = get_multiple_iv_ibkr(list(price_filtered.keys()), ib)
    iv_results = {}
    for t in price_filtered:
        iv = iv_data.get(t)
        if iv is None:
            print(f"  {t}: ⚠️ No IV")
            continue
        action = "🔼 SELL" if iv > 0.5 else "🔽 BUY"
        print(f"  {t}: IV = {iv} → {action}")
        iv_results[t] = {"IV": iv, "Action": action}

    if not iv_results:
        print("❌ No IV data available.")
        return pd.DataFrame()

    # שלב 3: סטוכסטי
    print("\n📊 Step 3: Calculating Stochastic Oscillator...")
    stoch_df = get_stochastic_signals(list(iv_results.keys()))
    if stoch_df.empty:
        print("❌ No tickers passed stochastic calculation.")
        return pd.DataFrame()

    # שלב 4: תמיכה / התנגדות
    print("\n📊 Step 4: Adding Support/Resistance Levels...")
    final_rows = []

    for _, row in stoch_df.iterrows():
        ticker = row['ticker']
        signal = row['signal']
        k = row['k']
        d = row['d']

        sr = get_support_resistance(ticker)
        sr_level = None
        sr_type = None
        if sr:
            if signal == 'Oversold' and sr['support']:
                sr_level = sr['support'][0]
                sr_type = 'Support'
            elif signal == 'Overbought' and sr['resistance']:
                sr_level = sr['resistance'][-1]
                sr_type = 'Resistance'

        iv_info = iv_results.get(ticker)
        if not iv_info:
            continue

        final_rows.append({
            "Symbol": ticker,
            "IV": iv_info["IV"],
            "Action": iv_info["Action"],
            "Signal": signal,
            "%K": k,
            "%D": d,
            sr_type: sr_level
        })

    df = pd.DataFrame(final_rows)
    print("\n✅ Final Evaluation:")
    print(df)

    return df



if __name__ == "__main__":
    fifthi_tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX', 'AMD', 'INTC',
                      'BA', 'WMT', 'DIS', 'T', 'KO', 'PEP', 'MCD', 'NKE', 'COST', 'SBUX',
                      'JPM', 'BAC', 'GS', 'WFC', 'MS', 'V', 'MA', 'PYPL', 'AXP', 'SQ',
                      'CVX', 'XOM', 'COP', 'SLB', 'F', 'GM', 'GE', 'CAT', 'DE', 'MMM',
                      'UNH', 'PFE', 'JNJ', 'MRK', 'ABT', 'TMO', 'LLY', 'CVS', 'BMY', 'AMGN']
    l=['AAPL', 'TSLA', 'MSFT', 'GOOG', 'AMD', 'NVDA', 'INTC']
    final = get_filtered_stocks(fifthi_tickers,ib)
    print("\n📈 Final selected tickers:", final)
    ib.disconnect()
