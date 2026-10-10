"""Dual Thrust indicators (Michael Chalek's session-range breakout).

Session = one UTC day of 1h bars (24 bars). For each bar, the lookback is
the 5 complete prior sessions: over those bars compute
    HH = max(h), LC = min(c), HC = max(c), LL = min(l)
    Range = max(HH - LC, HC - LL)
day_open = open of the first bar of the current UTC day.
    BuyLine  = day_open + K1 * Range
    SellLine = day_open - K2 * Range   (K1 = K2 = 0.7, module constants)
A session counts as complete only with a full 24 bars; incomplete days
poison the range to NaN (no signals) rather than bias the breakout level.
No lookahead: everything per bar uses only data through that bar's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

K1 = 0.7
K2 = 0.7
SESSIONS = 5
BARS_PER_SESSION = 24
MS_PER_DAY = 86_400_000


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    day = pd.Series((df["t"] // MS_PER_DAY).to_numpy(), index=df.index)
    df["day_open"] = df.groupby(day)["o"].transform("first")

    agg = pd.DataFrame(
        {
            "hmax": df.groupby(day)["h"].max(),
            "lmin": df.groupby(day)["l"].min(),
            "cmax": df.groupby(day)["c"].max(),
            "cmin": df.groupby(day)["c"].min(),
            "n": df.groupby(day)["c"].size(),
        }
    ).sort_index()
    complete = agg["n"] >= BARS_PER_SESSION
    hh = agg["hmax"].where(complete).shift(1).rolling(SESSIONS, min_periods=SESSIONS).max()
    lc = agg["cmin"].where(complete).shift(1).rolling(SESSIONS, min_periods=SESSIONS).min()
    hc = agg["cmax"].where(complete).shift(1).rolling(SESSIONS, min_periods=SESSIONS).max()
    ll = agg["lmin"].where(complete).shift(1).rolling(SESSIONS, min_periods=SESSIONS).min()
    dt_range = pd.Series(
        np.maximum((hh - lc).to_numpy(), (hc - ll).to_numpy()), index=agg.index
    )
    df["dt_range"] = day.map(dt_range).to_numpy(dtype=float)
    df["buy_line"] = df["day_open"] + K1 * df["dt_range"]
    df["sell_line"] = df["day_open"] - K2 * df["dt_range"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
