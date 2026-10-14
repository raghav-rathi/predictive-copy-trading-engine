"""TTM Squeeze indicators (John Carter, Mastering the Trade Ch. 11).

Squeeze = Bollinger Bands(20, 2.0) entirely inside Keltner Channel
(20-EMA, 1.5 x ATR(14)): bb_upper < kc_upper AND bb_lower > kc_lower.
The signal is the RELEASE: the first bar BB expands back outside KC
after >= 5 consecutive squeeze bars. Direction comes from the momentum
histogram = linear-regression slope of (c - typical price) over 12 bars:
rising -> long, falling -> short. No lookahead: every rolling value uses
only bars through the current close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0
KC_EMA_N = 20
ATR_N = 14
KC_K = 1.5
SQUEEZE_MIN_BARS = 5
MOM_N = 12


def _linreg_slope(s: pd.Series, n: int) -> pd.Series:
    x = np.arange(n)

    def f(y):
        if np.isnan(y).any():
            return np.nan
        return float(np.polyfit(x, y, 1)[0])

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
    # consecutive squeeze-bar run length ending at the current bar
    sq = df["squeeze"].to_numpy(dtype=bool)
    cnt = np.zeros(len(sq), dtype=int)
    run = 0
    for i, v in enumerate(sq):
        run = run + 1 if v else 0
        cnt[i] = run
    df["squeeze_count"] = cnt
    mom_input = df["c"] - (df["h"] + df["l"] + df["c"]) / 3
    df["mom_hist"] = _linreg_slope(mom_input, MOM_N)
    df["mom_rising"] = (df["mom_hist"] > df["mom_hist"].shift(1)).fillna(False)
    df["mom_falling"] = (df["mom_hist"] < df["mom_hist"].shift(1)).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
