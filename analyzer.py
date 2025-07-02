import pandas as pd
import pandas_ta as ta
from scipy.signal import argrelextrema
import numpy as np

class Analyzer:
    """Calculate technical indicators on price data."""

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["RSI"] = ta.rsi(df["Close"], length=14)
        df["SMA"] = ta.sma(df["Close"], length=20)
        df["EMA"] = ta.ema(df["Close"], length=20)
        macd = ta.macd(df["Close"], fast=12, slow=26, signal=9)
        df = pd.concat([df, macd], axis=1)
        return df

    def support_resistance(self, df: pd.DataFrame, order: int = 5):
        df = df.copy()
        df['min'] = df['Low'].iloc[argrelextrema(df['Low'].values, np.less_equal, order=order)[0]]
        df['max'] = df['High'].iloc[argrelextrema(df['High'].values, np.greater_equal, order=order)[0]]
        support = df['min'].dropna().tolist()
        resistance = df['max'].dropna().tolist()
        return support, resistance
