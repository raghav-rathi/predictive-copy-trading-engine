"""NR7 indicators (Toby Crabel, "Day Trading with Short Term Price Patterns").

NR7 = narrowest range of the last 7 bars: on bar i,
    is_nr7[i] = range[i] == min(range[i-6 .. i])  (inclusive window),
where range = h - l. Compression flags a volatility contraction; Crabel's
setup trades the break of the NR7 bar's extremes in either direction.
No lookahead: the rolling minimum uses only bars through the current bar.
"""

import pandas as pd

NR7_WINDOW = 7
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    from strategies import base as B

    df = df.copy()
    df["rng"] = df["h"] - df["l"]
    roll_min = df["rng"].rolling(NR7_WINDOW, min_periods=NR7_WINDOW).min()
    df["is_nr7"] = (df["rng"] == roll_min).fillna(False)
    df["nr7_high"] = df["h"].where(df["is_nr7"])
    df["nr7_low"] = df["l"].where(df["is_nr7"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
