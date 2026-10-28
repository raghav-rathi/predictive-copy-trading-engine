"""Keltner breakout + RSI-band confirmation signals.

    long_entry  -- close breaks above the Keltner upper band AND
                   RSI(14) is in [50, 75] (momentum confirmed, not yet
                   overbought)
    short_entry -- close breaks below the Keltner lower band AND
                   RSI(14) is in [25, 50]
    long_exit   -- close crosses back below the Keltner mid-band
    short_exit  -- close crosses back above the Keltner mid-band

The RSI band is the filter that keeps the strategy out of the two
failure modes of a bare channel breakout: dead chop (RSI near 50
with no direction is excluded by the breakout itself) and vertical
blow-offs (RSI above 75 / below 25, where breakouts most often
reverse). Entries are level conditions, not crosses: the breakout
bar and any continuation bar above the band with RSI in range both
qualify, and the backtest holds one position at a time, so repeats
while in a position are inert. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    rsi = df["rsi"]
    long_cond = (c > df["kc_upper"]) & (rsi >= 50) & (rsi <= 75)
    short_cond = (c < df["kc_lower"]) & (rsi >= 25) & (rsi <= 50)
    df["long_entry"] = long_cond.fillna(False).astype(bool)
    df["short_entry"] = short_cond.fillna(False).astype(bool)
    df["long_exit"] = crossed_below(c, df["kc_mid"]).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(c, df["kc_mid"]).fillna(False).astype(bool)
    return df
