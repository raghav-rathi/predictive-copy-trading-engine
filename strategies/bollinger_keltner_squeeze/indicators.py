"""John Carter TTM Squeeze indicators.

Bollinger Bands BB(20, 2) around SMA(20) vs Keltner Channels
KC(20, 1.5 x ATR(14)) around EMA(20). The squeeze is ON when the
Bollinger Bands sit strictly inside the Keltner Channels:

    squeeze_on  iff  bb_upper < kc_upper AND bb_lower > kc_lower

Momentum histogram: let x = close - ((20-bar high + 20-bar low)/2
+ SMA(20)) / 2, i.e. close minus the midpoint of the 20-bar
high-low midpoint and the 20-bar SMA. The momentum value on bar i
is the fitted value at bar i of the 20-bar linear regression of x
(mean + slope * 9.5, with the slope from the closed-form OLS
formula over the trailing 20 bars).

Columns:
    bb_mid / bb_upper / bb_lower -- Bollinger Bands
    kc_mid / kc_upper / kc_lower -- Keltner Channels
    squeeze_on -- bool, True while the bands are inside the channels
    momentum -- TTM-style momentum (regression fitted value)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. Rolling windows are trailing (include bar i, exclude later
bars); the regression is fit on the trailing 20 values of x.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0
KC_N = 20
KC_MULT = 1.5
ATR_N = 14
MOM_N = 20


def add_indicators(df: pd.DataFrame, bb_n: int = BB_N, bb_k: float = BB_K,
                   kc_n: int = KC_N, kc_mult: float = KC_MULT,
                   atr_n: int = ATR_N, mom_n: int = MOM_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    h = df["h"]
    l = df["l"]
    n = len(df)

    sma = B.sma(c, bb_n)
    sd = c.rolling(bb_n, min_periods=bb_n).std()
    df["bb_mid"] = sma
    df["bb_upper"] = sma + bb_k * sd
    df["bb_lower"] = sma - bb_k * sd

    kc_mid = B.ema(c, kc_n)
    a = B.atr(h, l, c, atr_n)
    df["kc_mid"] = kc_mid
    df["kc_upper"] = kc_mid + kc_mult * a
    df["kc_lower"] = kc_mid - kc_mult * a
    df["atr"] = a

    df["squeeze_on"] = (
        (df["bb_upper"] < df["kc_upper"])
        & (df["bb_lower"] > df["kc_lower"])
    ).fillna(False).astype(bool)

    # ---- TTM momentum: 20-bar linreg fitted value of x ----
    hh = h.rolling(mom_n, min_periods=mom_n).max()
    ll = l.rolling(mom_n, min_periods=mom_n).min()
    sma_mom = B.sma(c, mom_n)
    x = c - ((hh + ll) / 2 + sma_mom) / 2
    y = x.to_numpy(dtype=float)
    idx = np.arange(n, dtype=float)
    # sum(t*y) over the trailing window, t = 0..mom_n-1 within window:
    # sum(t*y) = sum(i*y) - s*sum(y), s = window start index.
    s1 = pd.Series(y).rolling(mom_n, min_periods=mom_n).sum().to_numpy(dtype=float)
    s2 = pd.Series(idx * y).rolling(mom_n, min_periods=mom_n).sum().to_numpy(dtype=float)
    s = idx - mom_n + 1
    tbar = (mom_n - 1) / 2.0
    denom = mom_n * (mom_n * mom_n - 1) / 12.0  # sum (t - tbar)^2
    slope = ((s2 - s * s1) - tbar * s1) / denom
    ybar = s1 / mom_n
    fitted = ybar + slope * tbar  # fitted value at t = mom_n - 1
    df["momentum"] = fitted
    return df
