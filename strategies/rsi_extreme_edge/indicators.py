"""RSI(14) + ATR(14) for the RSI extreme-edge fade system.

Raw RSI(14) and ATR(14) (Wilder). The excursion tracking (which bar pushed
RSI past the extreme, used by the structural-stop calibration variant) is
built in the calibration script, not here — indicators stay network-free
and lookahead-free.
"""

import pandas as pd

from strategies import base as B

RSI_N = 14
ATR_N = 14
RSI_SHORT_LEVEL = 90.0
RSI_LONG_LEVEL = 10.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], RSI_N)
    df["rsi_prev"] = df["rsi"].shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
