"""TTM-style squeeze breakout signals, long/short symmetric.

Entry logic (mirror for shorts):

    squeeze_recent = squeeze_on true at any of bars j-2..j
    long_entry  = squeeze_recent & crossed_above(close, bb_upper)
    short_entry = squeeze_recent & crossed_below(close, bb_lower)

The squeeze is a compression regime, not a trade: entering while
the squeeze is merely on catches every false twitch inside the
range. The entry therefore demands a breakout — a close outside
the Bollinger Band — shortly after compression (within the last
3 bars, so a squeeze that fired and released a bar or two ago
still counts, but a stale squeeze from a week ago does not).

Exits are the opposite-band crosses:

    long_exit  = crossed_below(close, bb_lower)
    short_exit = crossed_above(close, bb_upper)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

SQUEEZE_LOOKBACK = 3  # squeeze must have been on within the last 3 bars


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    upper = df["bb_upper"]
    lower = df["bb_lower"]
    squeeze = df["squeeze_on"].fillna(False).astype(bool)
    recent = (
        squeeze.rolling(SQUEEZE_LOOKBACK, min_periods=1).max() > 0
    ).fillna(False)

    xup = crossed_above(c, upper).fillna(False)
    xdn = crossed_below(c, lower).fillna(False)

    df["long_entry"] = (recent & xup).astype(bool)
    df["short_entry"] = (recent & xdn).astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
