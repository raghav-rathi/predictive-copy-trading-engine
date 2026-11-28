"""Popgun bar-pattern indicators (Jeffrey Kennedy).

    inside   -- h[i] < h[i-1] AND l[i] > l[i-1]
    outside  -- h[i] > h[i-1] AND l[i] < l[i-1]
    popgun   -- inside[i-1] AND outside[i]: an inside bar
                followed by an outside bar that engulfs it
    popgun_high / popgun_low -- the armed bracket: the
                high/low of the most recent popgun's outside
                bar, live from that bar through the next 5
                bars (the popgun bar itself included in the
                column for cross-detection -- a close can
                never cross above the high of its own bar).
                A newer popgun re-arms the bracket (replaces
                the old levels and restarts the 5-bar clock).
                After expiry both columns are NaN.
    popgun_armed -- a bracket is live on this bar
    atr14    -- Wilder ATR(14) for risk

No lookahead: inside/outside compare the current bar only
against the preceding bar; the bracket state machine only
reads bars up to the current one.
"""

import numpy as np
import pandas as pd

from strategies import base as B

VALIDITY_BARS = 5
ATR_N = 14


def add_indicators(
    df: pd.DataFrame,
    validity_bars: int = VALIDITY_BARS,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    n = len(df)
    inside = np.zeros(n, dtype=bool)
    outside = np.zeros(n, dtype=bool)
    for i in range(1, n):
        inside[i] = h[i] < h[i - 1] and l[i] > l[i - 1]
        outside[i] = h[i] > h[i - 1] and l[i] < l[i - 1]
    popgun = np.zeros(n, dtype=bool)
    popgun[1:] = inside[:-1] & outside[1:]
    df["inside"] = inside
    df["outside"] = outside
    df["popgun"] = popgun
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)

    high_col = np.full(n, np.nan)
    low_col = np.full(n, np.nan)
    armed_high = np.nan
    armed_low = np.nan
    armed_until = -1  # last index the bracket is live on
    for i in range(n):
        if popgun[i]:
            # A newer popgun re-arms the bracket (replaces the old one).
            armed_high = h[i]
            armed_low = l[i]
            armed_until = i + validity_bars
        if i <= armed_until:
            high_col[i] = armed_high
            low_col[i] = armed_low
        else:
            armed_high = np.nan
            armed_low = np.nan
    df["popgun_high"] = high_col
    df["popgun_low"] = low_col
    df["popgun_armed"] = ~np.isnan(high_col)
    return df
