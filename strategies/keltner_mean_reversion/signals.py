"""Keltner channel mean-reversion signals (Linda Raschke fade).

Long entry: the close CROSSES BELOW the lower Keltner band
(cross-based, so it fires once per band tag, not every bar
the close sits below the band) AND the entry bar is a
bullish candle (close > open) -- the first sign buyers are
stepping in at the stretched band.

Short entry: mirror -- close crosses above the upper band
AND the bar is a bearish candle (close < open).

Exit: long exits when the close crosses above the midline
(the mean-reversion target) or on the opposite entry;
short mirrors (close crosses below the midline). The house
2xATR hard stop / 3xATR trail sit behind these exits, with
a 72-bar max hold.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    o = df["o"]
    long_entry = (
        crossed_below(c, df["kc_lower"]) & (c > o)
    ).fillna(False)
    short_entry = (
        crossed_above(c, df["kc_upper"]) & (c < o)
    ).fillna(False)
    long_exit = (
        crossed_above(c, df["kc_mid"]) | short_entry
    ).fillna(False)
    short_exit = (
        crossed_below(c, df["kc_mid"]) | long_entry
    ).fillna(False)
    df["long_entry"] = long_entry.to_numpy(bool)
    df["short_entry"] = short_entry.to_numpy(bool)
    df["long_exit"] = long_exit.to_numpy(bool)
    df["short_exit"] = short_exit.to_numpy(bool)
    return df
