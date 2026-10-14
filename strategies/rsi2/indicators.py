"""RSI(2) mean-reversion indicators (Larry Connors).

Rules (public: Connors & Raschke, "Short Term Trading Strategies That Work"):
  * trend filter: close above/below SMA(200)
  * long pullback:  RSI(2) < 10  (short: RSI(2) > 90)
  * exit: close crosses back through SMA(5), or RSI(2) extreme unwind
"""

import pandas as pd

from strategies import base as B

RSI_N = 2
TREND_N = 200
EXIT_N = 5
RSI_LONG_ENTRY = 10.0
RSI_SHORT_ENTRY = 90.0
RSI_LONG_EXIT = 85.0
RSI_SHORT_EXIT = 15.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi2"] = B.rsi(df["c"], RSI_N)
    df["sma200"] = B.sma(df["c"], TREND_N)
    df["sma5"] = B.sma(df["c"], EXIT_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
