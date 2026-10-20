"""OU half-life z-score mean-reversion indicators.

Deviation from the mean on log prices, with the mean-reversion speed
estimated causally each bar:

* dev(i) = log(c(i)) - SMA(log(c), 50)(i)
* AR(1) fit on the trailing 100 dev values: regress dev.diff() on
  dev.shift(1). Vectorized with rolling moments over 100-bar windows
  (cov(x,y) = E[xy] - E[x]E[y]; var(x) = E[x^2] - E[x]^2) so every
  value is recomputed from trailing data only — fully causal, O(n).
* theta = cov/var; half-life HL = -ln(2)/theta.
* A bar is tradable only when theta < 0 (mean-reverting) and
  5 <= HL <= 120; otherwise no signal.
* z(i) = dev(i) / rolling_std(dev, 50)(i).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEV_SPAN = 50  # SMA span for the log-price deviation
AR_SPAN = 100  # trailing bars in the per-bar AR(1) fit
STD_SPAN = 50  # rolling std span for the z-score
HL_MIN = 5.0  # half-life validity band
HL_MAX = 120.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    logc = np.log(df["c"].astype(float))

    dev = logc - logc.rolling(DEV_SPAN, min_periods=DEV_SPAN).mean()

    x = dev.shift(1)  # dev(t-1)
    y = dev.diff()  # dev(t) - dev(t-1)

    mx = x.rolling(AR_SPAN, min_periods=AR_SPAN).mean()
    my = y.rolling(AR_SPAN, min_periods=AR_SPAN).mean()
    cov = (x * y).rolling(AR_SPAN, min_periods=AR_SPAN).mean() - mx * my
    varx = (x * x).rolling(AR_SPAN, min_periods=AR_SPAN).mean() - mx * mx

    theta = cov / varx.replace(0.0, np.nan)
    half_life = -np.log(2.0) / theta
    valid = (
        (theta < 0.0)
        & (half_life >= HL_MIN)
        & (half_life <= HL_MAX)
    ).fillna(False)

    std = dev.rolling(STD_SPAN, min_periods=STD_SPAN).std()
    z = dev / std.replace(0.0, np.nan)

    out["dev"] = dev
    out["theta"] = theta
    out["half_life"] = half_life
    out["hl_valid"] = valid.astype(bool)
    out["zscore"] = z
    return out
