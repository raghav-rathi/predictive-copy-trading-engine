"""Negative/Positive Volume Index indicators (Dysart / Fosback).

NVI updates only when volume DECREASES bar-over-bar (the "smart money"
read: quiet accumulation); PVI updates only when volume INCREASES (the
crowd read). Both accumulate percentage price change multiplicatively
from a 1000 base:

  NVI[i] = NVI[i-1] * (1 + pct[i])  if v[i] < v[i-1], else NVI[i-1]
  PVI[i] = PVI[i-1] * (1 + pct[i])  if v[i] > v[i-1], else PVI[i-1]

Fosback's signal: NVI above its long moving average = bull regime.
Ported from the classic 255-DAY EMA to 255 1h bars (~10.6 days) with the
port noted — the bar count, not the calendar span, is what survives.
No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDEX_EMA = 255


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    v = df["v"]
    pct = c.pct_change().fillna(0.0).to_numpy()
    vv = v.to_numpy()
    vprev = np.concatenate([[vv[0]], vv[:-1]])
    nvi_mult = np.where(vv < vprev, 1.0 + pct, 1.0)
    pvi_mult = np.where(vv > vprev, 1.0 + pct, 1.0)
    df["nvi"] = 1000.0 * pd.Series(nvi_mult, index=df.index).cumprod()
    df["pvi"] = 1000.0 * pd.Series(pvi_mult, index=df.index).cumprod()
    df["nvi_ema"] = B.ema(df["nvi"], INDEX_EMA)
    df["pvi_ema"] = B.ema(df["pvi"], INDEX_EMA)
    return df
