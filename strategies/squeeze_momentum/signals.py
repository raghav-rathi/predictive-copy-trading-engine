"""LazyBear Squeeze Momentum signals.

LONG entry on squeeze release, all on bar i:

- squeeze released (bands inside the channels on bar i-1, outside
  on bar i),
- momentum rising AND positive,
- momentum at its trailing-100-bar low,
- close above EMA(100) and above the prior bar's close.

SHORT entry is the mirror: release, momentum falling and
negative, momentum at its trailing-100-bar high, close below
EMA(100) and below the prior close.

Exit: long exits on the first bar momentum starts falling
(first downtick of the histogram); short exits on the first
uptick. The 2xATR(14) harness stop is the backstop. All
conditions read data through bar i; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    release = df["squeeze_release"].fillna(False)
    long_entry = (
        release
        & df["mom_rising"].fillna(False)
        & (df["mom"] > 0)
        & df["mom_100_low"].fillna(False)
        & (c > df["ema100"])
        & (c > c.shift(1))
    ).fillna(False)
    short_entry = (
        release
        & df["mom_falling"].fillna(False)
        & (df["mom"] < 0)
        & df["mom_100_high"].fillna(False)
        & (c < df["ema100"])
        & (c < c.shift(1))
    ).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = df["mom_falling"].fillna(False).astype(bool)
    df["short_exit"] = df["mom_rising"].fillna(False).astype(bool)
    return df
