"""Grid trading signals (classic range grid).

Long entry:  close in the BOTTOM 20% of the grid range
             (grid_pos <= 0.20) — buy the dip of the range.
Long exit:   close reaches the range midpoint (grid_pos >= 0.50).
Short entry: close in the TOP 20% of the grid range
             (grid_pos >= 0.80) — sell the top of the range.
Short exit:  close falls back to the range midpoint.

Entries are level conditions (not crosses): while the close sits in
a grid edge zone the signal stays on, so the harness re-enters after
a stop/trail exit as long as price is still in the zone — the
single-position approximation of a grid that would otherwise hold
one order per level. The harness risk layer's 2xATR stop / 2.5xATR
trail also applies. Signal columns are boolean, no NaN, no
lookahead (the harness executes at the next bar's open).
"""

import pandas as pd

from strategies.grid_trading.indicators import BOTTOM_FRAC, TOP_FRAC


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pos = df["grid_pos"]
    mid = df["grid_mid"]
    long_entry = (pos <= BOTTOM_FRAC).fillna(False)
    short_entry = (pos >= TOP_FRAC).fillna(False)
    long_exit = (df["c"] >= mid).fillna(False)
    short_exit = (df["c"] <= mid).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
