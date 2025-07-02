import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from datetime import datetime

# התחברות למסד
client = MongoClient("mongodb://localhost:27017/")
db = client["trade_db"]
collection = db["historical_prices"]  # שמור בקולקציה ייעודית

# פונקציית המרה לפורמט מתאים
def doc_from_row(ticker, row):
    return {
        "ticker": ticker,
        "date": row.name.strftime("%Y-%m-%d"),
        "data": {
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        }
    }

# שמירת היסטוריה מלאה למניה
def save_full_history(ticker):
    print(f"⬇️ Fetching full history for {ticker} from Yahoo...")
    df = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False)

    if df.empty:
        print(f"⚠️ No data found for {ticker}")
        return

    count = 0
    for _, row in df.iterrows():
        date_str = row.name.strftime("%Y-%m-%d")
        query = {"ticker": ticker, "date": date_str}
        doc = doc_from_row(ticker, row)
        collection.update_one(query, {"$set": doc}, upsert=True)
        count += 1

    print(f"✅ Saved {count} daily records for {ticker}")

# שליפת מידע קיים והשגת מידע חסר
def get_data_with_gap_fill(ticker, start_date, end_date):
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # שליפת המידע הקיים במסד
    cursor = collection.find({
        "ticker": ticker,
        "date": {"$gte": start_str, "$lte": end_str}
    })

    existing_data = {doc["date"]: doc for doc in cursor}

    # בניית טווח תאריכים יומי
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    missing_dates = [d for d in all_dates if d.strftime("%Y-%m-%d") not in existing_data]

    # אם חסר – נמשוך מ־Yahoo רק את החסר
    if missing_dates:
        print(f"🔍 Missing {len(missing_dates)} days – fetching from Yahoo...")
        df = yf.download(ticker, start=missing_dates[0], end=missing_dates[-1] + pd.Timedelta(days=1), interval="1d", progress=False)

        for _, row in df.iterrows():
            doc = doc_from_row(ticker, row)
            collection.update_one(
                {"ticker": ticker, "date": doc["date"]},
                {"$set": doc},
                upsert=True
            )
            existing_data[doc["date"]] = doc

    # מיון לפי תאריך
    final_data = [existing_data[d.strftime("%Y-%m-%d")] for d in all_dates if d.strftime("%Y-%m-%d") in existing_data]
    return final_data
save_full_history("AAPL")
from datetime import datetime

data = get_data_with_gap_fill("AAPL", datetime(2018, 1, 1), datetime(2024, 12, 31))
print(f"📊 Retrieved {len(data)} records for AAPL")
