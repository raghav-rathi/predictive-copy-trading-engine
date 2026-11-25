"""Ichimoku Kumo (cloud) breakout signals.

Long when close crosses above the cloud top AND tenkan > kijun
(momentum agrees with the breakout); short when close crosses
below the cloud bottom AND tenkan < kijun. Exit when close
crosses back into the cloud: a long exits when close falls
below the cloud top, a short exits when close rises above the
cloud bottom. Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    top = df["cloud_top"]
    bottom = df["cloud_bottom"]
    df["long_entry"] = (
        crossed_above(c, top) & (df["tenkan"] > df["kijun"])
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        crossed_below(c, bottom) & (df["tenkan"] < df["kijun"])
    ).fillna(False).astype(bool)
    # level exits: close back inside (or through) the cloud
    df["long_exit"] = (c < top).fillna(False).astype(bool)
    df["short_exit"] = (c > bottom).fillna(False).astype(bool)
    return df
