"""LazyBear Squeeze Momentum indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Squeeze: Bollinger Bands (20, 2 sigma, SMA mid) inside
   Keltner Channels (20 EMA mid, 1.5xATR(14)). The squeeze is
   RELEASED on the first bar the bands move back outside the
   channels after being inside on the prior bar.
2. Linear-regression momentum (LazyBear): let x = close minus
   the average of (a) the midpoint of the trailing-20-bar high
   and low and (b) the 20-bar SMA of close. The momentum value
   is the fitted value at bar i of the 20-bar linear regression
   of x (mean + slope * 9.5). Rising/falling is the change vs
   bar i-1.
3. Momentum extreme: the momentum value is at its trailing
   100-bar low (long side) or high (short side).
4. Trend filter: close above/below EMA(100), and close above/
   below the prior bar's close.

Columns:

    bb_mid / bb_upper / bb_lower -- Bollinger Bands (20, 2)
    kc_mid / kc_upper / kc_lower -- Keltner Channels (20, 1.5xATR14)
    squeeze -- BB strictly inside KC on bar i
    squeeze_release -- squeeze on bar i-1, off on bar i
    mom -- linear-regression momentum (fitted value)
    mom_rising / mom_falling -- vs bar i-1
    mom_100_low / mom_100_high -- mom at its trailing-100-bar extreme
    ema100 -- EMA(100) trend filter
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every rolling window is trailing (includes bar i,
excludes later bars); the regression is fit on the trailing 20
values of x only. The momentum regression uses the same
closed-form OLS as the house TTM implementation, computed via
a rolling apply over the trailing window.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0
KC_EMA_N = 20
ATR_N = 14
KC_K = 1.5
MOM_N = 20
EXTREME_N = 100
EMA_N = 100


def _linreg_fitted(s: pd.Series, n: int) -> pd.Series:
    """Fitted value at the last point of a trailing n-bar OLS fit."""
    x = np.arange(n, dtype=float)

    def f(y):
        if np.isnan(y).any():
            return np.nan
        slope, intercept = np.polyfit(x, y, 1)
        return float(intercept + slope * (n - 1))

    return s.rolling(n, min_periods=n).apply(f, raw=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], BB_N, BB_K)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    kc = B.keltner(df["h"], df["l"], df["c"], ema_n=KC_EMA_N, atr_n=ATR_N, k=KC_K)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    squeeze = (df["bb_upper"] < df["kc_upper"]) & (df["bb_lower"] > df["kc_lower"])
    df["squeeze"] = squeeze.fillna(False)
    df["squeeze_release"] = (
        df["squeeze"].shift(1).fillna(False) & ~df["squeeze"]
    )
    mid_hl = (df["h"].rolling(MOM_N, min_periods=MOM_N).max()
              + df["l"].rolling(MOM_N, min_periods=MOM_N).min()) / 2
    mom_input = df["c"] - (mid_hl + B.sma(df["c"], MOM_N)) / 2
    df["mom"] = _linreg_fitted(mom_input, MOM_N)
    df["mom_rising"] = (df["mom"] > df["mom"].shift(1)).fillna(False)
    df["mom_falling"] = (df["mom"] < df["mom"].shift(1)).fillna(False)
    df["mom_100_low"] = (
        df["mom"] <= df["mom"].rolling(EXTREME_N, min_periods=EXTREME_N).min()
    ).fillna(False)
    df["mom_100_high"] = (
        df["mom"] >= df["mom"].rolling(EXTREME_N, min_periods=EXTREME_N).max()
    ).fillna(False)
    df["ema100"] = B.ema(df["c"], EMA_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
