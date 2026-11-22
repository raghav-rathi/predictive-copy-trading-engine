"""BTC Breakout Trend Climber signals.

LONG entry on a breakout cross, either leg of the source's OR:

- close crosses above the prior-600-bar highest high (25-day
  Donchian breakout), OR
- close crosses above the upper Bollinger Band (50, 2.1 sigma,
  EMA mid).

SHORT entry is the mirror: close crosses below the prior-600-bar
lowest low, or below the lower Bollinger Band.

Exits are the opposite breakout: a short breakout while long
exits the long (and opens the short — the harness flips), and
vice versa. The ATR-staged stop/trail in risk.py does the rest
of the trade management. All conditions read closes and levels
through bar i; the harness executes at the next bar's open.
Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    long_break = B.crossed_above(c, df["donch_high_600"]) | B.crossed_above(
        c, df["bb_upper"]
    )
    short_break = B.crossed_below(c, df["donch_low_600"]) | B.crossed_below(
        c, df["bb_lower"]
    )
    df["long_entry"] = long_break.fillna(False).astype(bool)
    df["short_entry"] = short_break.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
