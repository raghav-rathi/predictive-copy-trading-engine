"""Klinger Volume Oscillator indicators (Stephen Klinger).

Canonical construction:
  tp   = (h + l + c) / 3                        typical price
  trend = +1 if tp > tp.shift(1) else -1        direction of the bar
  dm   = h - l                                  bar range
  cm   = cumulative range: cm[i] = cm[i-1] + dm[i] when the trend did not
         change between bars i-1 and i, otherwise dm[i-1] + dm[i]
         (numpy loop, seeded with cm[0] = dm[0])
  VF   = v * (2 * (dm / cm) - 1) * trend * 100  volume force (cm == 0 -> 0)
  kvo  = EMA(VF, 34) - EMA(VF, 55)              the oscillator
  ksig = EMA(kvo, 13)                          the signal line

The cm loop is the only non-vectorizable part: each bar's cumulative
range depends on whether the trend persisted from the previous bar.
All series are causal (bar i uses only bars <= i); the harness executes
at bar i+1's open.
"""

import numpy as np
import pandas as pd

from strategies.base import ema

FAST_N = 34
SLOW_N = 55


def add_indicators(df: pd.DataFrame, kvo_fast: int = 34,
                   kvo_slow: int = 55, signal_n: int = 13) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    if n == 0:
        for col in ("tp", "trend", "dm", "cm", "vf", "kvo", "ksig"):
            df[col] = np.nan
        return df

    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    trend = np.where(tp.to_numpy() > tp.shift(1).to_numpy(), 1.0, -1.0)
    dm = (df["h"] - df["l"]).to_numpy()

    # cumulative range, seeded with cm[0] = dm[0]
    cm = np.empty(n)
    cm[0] = dm[0]
    for i in range(1, n):
        if trend[i] == trend[i - 1]:
            cm[i] = cm[i - 1] + dm[i]
        else:
            cm[i] = dm[i - 1] + dm[i]

    vf = np.where(
        cm != 0.0,
        df["v"].to_numpy() * (2.0 * (dm / np.where(cm != 0.0, cm, 1.0)) - 1.0) * trend * 100.0,
        0.0,
    )

    kvo = ema(pd.Series(vf, index=df.index), kvo_fast) - ema(
        pd.Series(vf, index=df.index), kvo_slow
    )
    ksig = ema(kvo, signal_n)

    df["tp"] = tp
    df["trend"] = trend
    df["dm"] = dm
    df["cm"] = cm
    df["vf"] = vf
    df["kvo"] = kvo
    df["ksig"] = ksig
    return df
