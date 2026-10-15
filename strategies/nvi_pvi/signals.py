"""NVI/PVI signals (Fosback).

Primary trigger is the NVI crossing its 255-bar EMA (smart-money regime
flip); the PVI must agree (above its own EMA for longs, below for
shorts) so crowd flow isn't fighting the entry:
  long_entry:  NVI crosses above NVI_EMA and PVI > PVI_EMA
  short_entry: NVI crosses below NVI_EMA and PVI < PVI_EMA
Exits: NVI crosses back through its EMA (regime call revoked).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    nvi, nvi_ema = df["nvi"], df["nvi_ema"]
    pvi, pvi_ema = df["pvi"], df["pvi_ema"]
    df["long_entry"] = (B.crossed_above(nvi, nvi_ema) & (pvi > pvi_ema)).fillna(False)
    df["short_entry"] = (B.crossed_below(nvi, nvi_ema) & (pvi < pvi_ema)).fillna(False)
    df["long_exit"] = B.crossed_below(nvi, nvi_ema).fillna(False)
    df["short_exit"] = B.crossed_above(nvi, nvi_ema).fillna(False)
    return df
