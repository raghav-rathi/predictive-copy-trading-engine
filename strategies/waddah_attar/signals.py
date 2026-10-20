"""Waddah Attar Explosion signals.

Long entry (all true on bar i, execution at bar i+1 open):
  hist > 0 AND hist rising AND hist > explosion AND explosion rising
  AND hist > dead AND explosion > dead.

Short entry mirrors with hist < 0 and a falling histogram.

Exits: long exits when the histogram crosses back below the explosion
line (momentum died); short exits when the histogram crosses back
above the negative explosion line (symmetric: |hist| < explosion).

Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hist = df["wae_hist"]
    expl = df["wae_expl"]
    dead = df["wae_dead"]
    hist_rising = df["wae_hist_rising"].fillna(False)
    expl_rising = df["wae_expl_rising"].fillna(False)

    long_entry = (
        (hist > 0)
        & hist_rising
        & (hist > expl)
        & expl_rising
        & (hist > dead)
        & (expl > dead)
    )
    short_entry = (
        (hist < 0)
        & ~hist_rising
        & (-hist > expl)
        & expl_rising
        & (-hist > dead)
        & (expl > dead)
    )
    long_exit = (hist < expl) & (hist.shift(1) >= expl.shift(1))
    short_exit = (hist > -expl) & (hist.shift(1) <= -expl.shift(1))

    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
