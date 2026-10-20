"""SSL Channel regime-flip signals.

Regime state: +1 (bullish) when close crosses above the active SSL
line (close > ssl_up), -1 (bearish) when close crosses below it
(close < ssl_dn); otherwise the prior state is held. The "active line"
is the SSL line belonging to the current state, so a flip is a genuine
close-vs-line cross, not a band touch.

Long entry on the flip to bullish, short entry on the flip to bearish;
exits are the opposite flip (the channel manages the trade).

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull_raw = df["c"] > df["ssl_up"]
    bear_raw = df["c"] < df["ssl_dn"]
    raw = pd.Series(
        np.where(bull_raw, 1.0, np.where(bear_raw, -1.0, np.nan)),
        index=df.index,
    )
    state = raw.ffill().fillna(0.0)
    df["ssl_state"] = state
    prev = state.shift(1).fillna(0.0)
    long_entry = (state == 1.0) & (prev != 1.0)
    short_entry = (state == -1.0) & (prev != -1.0)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = short_entry.astype(bool)
    df["short_exit"] = long_entry.astype(bool)
    return df
