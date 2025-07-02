import sqlite3
from pathlib import Path
import pandas as pd

class Database:
    """Simple SQLite wrapper for storing OHLCV data."""
    def __init__(self, db_path: str = "market.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                ticker TEXT,
                ts TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (ticker, ts)
            )
            """
        )
        self.conn.commit()

    def insert_dataframe(self, ticker: str, df: pd.DataFrame):
        records = []
        for ts, row in df.iterrows():
            records.append((ticker, ts.strftime("%Y-%m-%d %H:%M:%S"), float(row["Open"]),
                            float(row["High"]), float(row["Low"]), float(row["Close"]), int(row["Volume"])) )
        self.conn.executemany(
            "INSERT OR REPLACE INTO prices VALUES (?, ?, ?, ?, ?, ?, ?)",
            records,
        )
        self.conn.commit()

    def fetch_dataframe(self, ticker: str, limit: int = 100):
        query = "SELECT ts, open, high, low, close, volume FROM prices WHERE ticker=? ORDER BY ts DESC LIMIT ?"
        rows = self.conn.execute(query, (ticker, limit)).fetchall()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
        df["ts"] = pd.to_datetime(df["ts"])
        df.set_index("ts", inplace=True)
        return df.sort_index()
