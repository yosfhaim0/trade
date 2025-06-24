import yfinance as yf
import pandas as pd
from scipy.signal import argrelextrema
import numpy as np

def get_support_resistance(ticker, period='6mo', order=5):
    df = yf.download(ticker, period=period, interval='1d', progress=False)
    if df.empty:
        return None

    df['Min'] = df['Low'].iloc[argrelextrema(df['Low'].values, np.less_equal, order=order)[0]]
    df['Max'] = df['High'].iloc[argrelextrema(df['High'].values, np.greater_equal, order=order)[0]]

    support_levels = sorted(df['Min'].dropna().round(2).unique().tolist())
    resistance_levels = sorted(df['Max'].dropna().round(2).unique().tolist())

    return {
        'ticker': ticker,
        'period': period,
        'support': support_levels,
        'resistance': resistance_levels
    }



def add_support_resistance_to_signals(signals_df):
    results = []

    for _, row in signals_df.iterrows():
        ticker = row['ticker']
        signal = row['signal']
        k = row['k']
        d = row['d']

        sr = get_support_resistance(ticker)
        if not sr:
            continue

        if signal == 'Overbought':
            level = sr['resistance'][-1] if sr['resistance'] else None
            label = 'Resistance'
        elif signal == 'Oversold':
            level = sr['support'][0] if sr['support'] else None
            label = 'Support'
        else:
            continue

        results.append({
            'Symbol': ticker,
            'Signal': signal,
            'K': k,
            'D': d,
            label: level
        })

    return pd.DataFrame(results)
if __name__ == '__main__':

    result = get_support_resistance('AAPL', period='6mo', order=3)
    print(result)

    # חיפוש אם 180 מופיע
    if 180 in result['support']:
        print("✅ 180 נמצא כרמת תמיכה.")
    else:
        print("❌ 180 לא נמצא.")

