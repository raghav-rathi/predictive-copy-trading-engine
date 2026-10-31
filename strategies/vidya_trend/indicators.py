"""Tushar Chande Variable Index Dynamic Average (VIDYA).

CMO(9) = 100 * (UpSum - DnSum) / (UpSum + DnSum), where UpSum is the
sum of positive close-to-close changes and DnSum the sum of absolute
negative close-to-close changes over the 9 most recent changes (the
change ending at the current bar and the 8 before it). If
UpSum + DnSum == 0 (flat market), CMO = 0.
F = 2 / (20 + 1). alpha = F * |CMO| / 100.
VIDYA = alpha * close + (1 - alpha) * prev VIDYA, initialised to the
close at the first valid bar (bar 9).

All windows end at the current bar, so there is no lookahead.

Columns:
    vidya_cmo   -- Chande Momentum Oscillator, [-100, 100]
    vidya_alpha -- dynamic smoothing factor
    vidya       -- the adaptive average
    atr         -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

CMO_PERIOD = 9
EMA_PERIOD = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    n = len(df)

    delta = c.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    up_sum = gain.rolling(CMO_PERIOD, min_periods=CMO_PERIOD).sum()
    dn_sum = loss.rolling(CMO_PERIOD, min_periods=CMO_PERIOD).sum()
    denom = up_sum + dn_sum
    cmo = pd.Series(
        np.where(
            denom.to_numpy(dtype=float) == 0,
            0.0,
            100.0
            * (up_sum.to_numpy(dtype=float) - dn_sum.to_numpy(dtype=float))
            / np.where(
                denom.to_numpy(dtype=float) == 0, 1.0, denom.to_numpy(dtype=float)
            ),
        ),
        index=df.index,
    )
    # CMO is undefined before 9 changes exist (bar 9).
    cmo = cmo.where(up_sum.notna() & dn_sum.notna())

    f = 2.0 / (EMA_PERIOD + 1)
    alpha = f * cmo.abs() / 100.0

    cv = c.to_numpy(dtype=float)
    av = alpha.to_numpy(dtype=float)
    vidya = np.full(n, np.nan)
    first = np.where(np.isfinite(av))[0]
    if len(first):
        j = int(first[0])
        vidya[j] = cv[j]
        for i in range(j + 1, n):
            a = av[i]
            vidya[i] = a * cv[i] + (1.0 - a) * vidya[i - 1]

    df["vidya_cmo"] = cmo
    df["vidya_alpha"] = alpha
    df["vidya"] = vidya
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
