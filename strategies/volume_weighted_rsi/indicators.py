"""Volume-weighted RSI indicators.

Typical price per bar: tp = (h + l + c) / 3.
VWTP(14) = sum(tp * v over the last 14 bars) / sum(v over the last 14 bars),
a rolling volume-weighted price — bars where big volume traded count
more. VW-RSI is Wilder RSI(14) computed on that VWTP series.

Fallback: if the rolling 14-bar volume sum is exactly 0, VWTP falls
back to the plain close for that bar (a zero-volume window carries no
volume information). A window with fewer than 14 bars yet is NaN.

Columns:
    vwtp   -- rolling volume-weighted typical price
    vw_rsi -- Wilder RSI(14) on vwtp
    atr    -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only (rolling windows include bar i and exclude everything after it).
"""

import numpy as np
import pandas as pd

from strategies import base as B

VWTP_WINDOW = 14
RSI_PERIOD = 14

INDICATOR_COLS = ["vwtp", "vw_rsi", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    vol = df["v"]
    sum_pv = (tp * vol).rolling(VWTP_WINDOW, min_periods=VWTP_WINDOW).sum()
    sum_v = vol.rolling(VWTP_WINDOW, min_periods=VWTP_WINDOW).sum()
    vwtp = sum_pv / sum_v.replace(0, np.nan)
    # Zero-volume window -> fall back to the plain close. A window
    # with < VWTP_WINDOW bars stays NaN (sum_v is NaN, not 0).
    vwtp = vwtp.mask(sum_v == 0, df["c"])
    df["vwtp"] = vwtp
    df["vw_rsi"] = B.rsi(vwtp, RSI_PERIOD)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
