"""NR7 volatility-expansion indicators (Toby Crabel narrow range).

    range   -- h - l of the bar
    nr7     -- range[i] is strictly less than each of
               range[i-6 .. i-1]: the narrowest range of the
               last 7 bars including the current one
    nr7_high / nr7_low -- the armed bracket: the high/low of
               the most recent NR7 bar, live from that bar
               through the next 3 bars (j+1 .. j+3, the NR7
               bar itself included in the column for
               cross-detection -- a close can never cross
               above the high of its own bar). A newer NR7
               re-arms the bracket (replaces the old levels
               and restarts the 3-bar clock). After expiry
               both columns are NaN.
    nr7_armed -- a bracket is live on this bar
    atr14   -- Wilder ATR(14) for risk

No lookahead: the NR7 test compares the current bar's range
only against the six preceding bars; ATR is Wilder
smoothing; the bracket state machine only reads bars up to
the current one.
"""

import numpy as np
import pandas as pd

from strategies import base as B

NR_N = 7
VALIDITY_BARS = 3
ATR_N = 14


def add_indicators(
    df: pd.DataFrame,
    nr_n: int = NR_N,
    validity_bars: int = VALIDITY_BARS,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    rng = (df["h"] - df["l"]).to_numpy(float)
    n = len(df)
    nr7 = np.zeros(n, dtype=bool)
    for i in range(nr_n - 1, n):
        # Strictly less than EACH of the previous nr_n - 1 ranges.
        if np.all(rng[i] < rng[i - nr_n + 1 : i]):
            nr7[i] = True
    df["nr_range"] = rng
    df["nr7"] = nr7
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)

    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    high_col = np.full(n, np.nan)
    low_col = np.full(n, np.nan)
    armed_high = np.nan
    armed_low = np.nan
    armed_until = -1  # last index the bracket is live on
    for i in range(n):
        if nr7[i]:
            # A newer NR7 re-arms the bracket (replaces the old one).
            armed_high = h[i]
            armed_low = l[i]
            armed_until = i + validity_bars
        if i <= armed_until:
            high_col[i] = armed_high
            low_col[i] = armed_low
        else:
            armed_high = np.nan
            armed_low = np.nan
    df["nr7_high"] = high_col
    df["nr7_low"] = low_col
    df["nr7_armed"] = ~np.isnan(high_col)
    return df
