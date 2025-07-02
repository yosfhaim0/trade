import yfinance as yf
from pymongo import MongoClient
from datetime import datetime
import pytz
import numpy as np

# הגדרות בסיסיות
DB_NAME = "trade_db"
COLLECTION_NAME = "trade_db"
TIMEZONE = "Asia/Jerusalem"

# התחברות למסד
client = MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# ממיר ערכים של numpy לסוגים רגילים
def convert_numpy_types(d):
    result = {}
    for k, v in d.items():
        if isinstance(v, (np.integer,)):
            result[k] = int(v)
        elif isinstance(v, (np.floating,)):
            result[k] = float(v)
        else:
            result[k] = v
    return result


def get_stock_data(tickers, force_update=False):
    today_str = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d")
    result = {}

    for ticker in tickers:
        print(f"🔎 Checking cache for {ticker}...")

        if not force_update:
            doc = collection.find_one({"ticker": ticker, "date": today_str})
            if doc:
                print(f"✅ Found cached data for {ticker}")
                result[ticker] = doc["data"]
                continue

        print(f"⏳ Downloading 6 months of data for {ticker}...")
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist.empty:
            print(f"⚠️  No data available for {ticker}")
            continue

        latest_data = None

        for date, row in hist.iterrows():
            date_str = date.strftime("%Y-%m-%d")

            raw_data = {
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
            }

            data = convert_numpy_types(raw_data)

            # שמירה למסד
            collection.update_one(
                {"ticker": ticker, "date": date_str},
                {"$set": {"data": data}},
                upsert=True
            )

            if date_str == today_str:
                latest_data = data

        print(f"💾 Saved 6-month history for {ticker}")

        if latest_data:
            result[ticker] = latest_data
        else:
            # אם אין דאטה מהיום – מחזיר את הנתון האחרון מההיסטוריה
            last_row = hist.iloc[-1]
            result[ticker] = convert_numpy_types({
                "open": last_row["Open"],
                "high": last_row["High"],
                "low": last_row["Low"],
                "close": last_row["Close"],
                "volume": last_row["Volume"],
            })

    return result


# דוגמה לשימוש
if __name__ == "__main__":
    a=['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX', 'AMD', 'INTC',
                      'BA', 'WMT', 'DIS', 'T', 'KO', 'PEP', 'MCD', 'NKE', 'COST', 'SBUX',
                      'JPM', 'BAC', 'GS', 'WFC', 'MS', 'V', 'MA', 'PYPL', 'AXP', 'SQ',
                      'CVX', 'XOM', 'COP', 'SLB', 'F', 'GM', 'GE', 'CAT', 'DE', 'MMM',
                      'UNH', 'PFE', 'JNJ', 'MRK', 'ABT', 'TMO', 'LLY', 'CVS', 'BMY', 'AMGN']
    tickers =  ['COIN']
    stock_data = get_stock_data(a,force_update=False)

    print("\n📊 Summary:")
    for ticker, data in stock_data.items():
        print(f"{ticker}: {data}")
