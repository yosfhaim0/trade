import pandas as pd
import pandas_ta as ta
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["trade_db"]
collection = db["trade_db"]

def analyze_ticker(ticker, rsi_period=14, stoch_k=10, stoch_d=3, stoch_smooth_k=3):
    cursor = collection.find({"ticker": ticker})
    records = []

    for doc in cursor:
        records.append({
            "date": doc["date"],
            "high": doc["data"]["high"],
            "low": doc["data"]["low"],
            "close": doc["data"]["close"]
        })

    if not records:
        return {"ticker": ticker, "error": "No data"}

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df.set_index("date", inplace=True)

    # RSI
    df["RSI"] = ta.rsi(df["close"], length=rsi_period)

    # Stochastic
    stoch = ta.stoch(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        k=stoch_k,
        d=stoch_d,
        smooth_k=stoch_smooth_k
    )
    df = df.join(stoch)

    latest = df.iloc[-1]
    rsi = latest["RSI"]
    k_val = latest[f"STOCHk_{stoch_k}_{stoch_smooth_k}_{stoch_d}"]
    d_val = latest[f"STOCHd_{stoch_k}_{stoch_smooth_k}_{stoch_d}"]

    # Interpret RSI
    rsi_status = (
        "📈 Overbought" if rsi > 70 else
        "📉 Oversold" if rsi < 30 else
        "🔄 Neutral"
    )

    # Interpret Stoch
    stoch_status = (
        "📈 Overbought" if k_val > 80 and d_val > 80 else
        "📉 Oversold" if k_val < 20 and d_val < 20 else
        "🔄 Neutral"
    )

    # Combined signal (optional)
    combined = (
        "📈 Overbought" if rsi > 70 and k_val > 80 and d_val > 80 else
        "📉 Oversold" if rsi < 30 and k_val < 20 and d_val < 20 else
        "🔄 Neutral"
    )

    return {
        "ticker": ticker,
        "RSI": round(rsi, 2),
        "RSI_status": rsi_status,
        "Stoch_K": round(k_val, 2),
        "Stoch_D": round(d_val, 2),
        "Stoch_status": stoch_status,
        "Combined": combined
    }
tickers = ["AAPL", "GOOG", "NVDA", "TSLA"]
results = [analyze_ticker(t) for t in tickers]

# הצגה מסודרת
print(f"{'Ticker':<6} {'RSI':<6} {'RSI Status':<15} {'K':<6} {'D':<6} {'Stoch Status':<15} {'Final'}")
for r in results:
    if "error" in r:
        print(f"{r['ticker']:<6} {r['error']}")
    else:
        print(f"{r['ticker']:<6} {r['RSI']:<6} {r['RSI_status']:<15} {r['Stoch_K']:<6} {r['Stoch_D']:<6} {r['Stoch_status']:<15} {r['Combined']}")
