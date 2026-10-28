"""RSI + MACD confluence signals.

    long_entry  -- RSI(14) crosses above 50 AND MACD histogram > 0
    short_entry -- RSI(14) crosses below 50 AND MACD histogram < 0
    long_exit   -- RSI(14) crosses back below 50
    short_exit  -- RSI(14) crosses back above 50

Neither indicator fires alone: the RSI 50-cross supplies the
momentum-regime change, and the histogram sign requires the MACD
to agree on trend direction at that moment, filtering RSI crosses
that happen while the MACD still points the other way. The exit
is the RSI recross alone (no histogram condition), so a position
is not held through a full momentum reversal waiting for MACD
agreement. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = df["rsi"]
    hist = df["macd_hist"]
    df["long_entry"] = (crossed_above(rsi, 50) & (hist > 0)).fillna(False).astype(bool)
    df["short_entry"] = (crossed_below(rsi, 50) & (hist < 0)).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(rsi, 50).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(rsi, 50).fillna(False).astype(bool)
    return df
