"""DeMark Trendline Breakout signals.

Tom DeMark TD trendlines: trendlines through the last two confirmed pivot highs (downtrend line) and last two confirmed pivot lows (uptrend line); pivots confirm with a 2-bar lag, so no lookahead. Long on close cross above the downtrend line, short on cross below the uptrend line; exits on the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["downtrend_line"]).fillna(False)
    down = B.crossed_below(df["c"], df["uptrend_line"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
