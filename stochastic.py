import pandas as pd
import yfinance as yf

def calculate_stochastic(df, k_period=10, d_period=3, smooth_k=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    k_fast = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    k_slow = k_fast.rolling(window=smooth_k).mean()
    d_slow = k_slow.rolling(window=d_period).mean()
    return k_slow, d_slow

def get_stochastic_signals(tickers, k_period=10, d_period=3, smooth_k=3):
    results = []

    for ticker in tickers:
        df = yf.download(ticker, period='6mo', interval='1d', progress=False)
        if df.empty or len(df) < k_period + d_period + smooth_k:
            continue

        k, d = calculate_stochastic(df, k_period, d_period, smooth_k)

        if k.dropna().empty or d.dropna().empty:
            continue

        latest_k = float(k.dropna().iloc[-1])
        latest_d = float(d.dropna().iloc[-1])

        if latest_k > 80 and latest_d > 80:
            results.append({
                'ticker': ticker,
                'signal': 'Overbought',
                'k': round(latest_k, 2),
                'd': round(latest_d, 2)
            })
        elif latest_k < 20 and latest_d < 20:
            results.append({
                'ticker': ticker,
                'signal': 'Oversold',
                'k': round(latest_k, 2),
                'd': round(latest_d, 2)
            })

    return pd.DataFrame(results)

# דוגמה לשימוש
if __name__ == "__main__":
    tickers = ['AAPL', 'TSLA', 'AMD', 'NVDA', 'MSFT', 'GOOG', 'META', 'AMZN']
    df_signals = get_stochastic_signals(tickers)
    print(df_signals)
