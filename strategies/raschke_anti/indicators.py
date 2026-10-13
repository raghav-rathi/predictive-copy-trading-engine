"""Raschke & Connors "Anti" (Street Smarts, Ch.9; 3/10/16 mechanics).

How this differs from the library's stoch_hook strategy (documented
deliberately, since both use stochastics):
  * stoch_hook defines trend by PRICE (close above/below EMA50) and enters
    on a slowK cross with rising flags.
  * raschke_anti defines trend by MOMENTUM: the slope of slow stochastic
    %D (7 %K, 10 %D). It then waits for a short-term counter-move AGAINST
    that trend -- fast %K hooks down through %D, or a 2-bar inside day
    (high below prior 2-bar high, low above prior 2-bar low) -- and only
    enters when short-term momentum re-aligns: fast %K turns back up
    through %D, OR the 3/10 oscillator (MACD(3,10)) crosses back above
    its 16-period signal in the trend direction. That 3/10/16 cross as a
    re-entry trigger is the published differentiator.
  * Protective stop goes below the pullback swing low; the backtest
    harness only supports static ATR stops, so 2.0xATR approximates it
    (documented in risk.py). Exit on the opposite setup or a chandelier
    trailing stop.

Pure pandas; no lookahead (arming uses only bars through i-1).
"""

import numpy as np
import pandas as pd

from strategies import base as B

K_PERIOD = 7
D_PERIOD = 10
FAST = 3
SLOW = 10
SIG = 16
ARM_WINDOW = 5
SLOPE_CONFIRM = 1  # consecutive rising %D bars required for trend


def add_indicators(
    df: pd.DataFrame,
    k: int = K_PERIOD,
    d: int = D_PERIOD,
    fast: int = FAST,
    slow: int = SLOW,
    sig: int = SIG,
    slope_confirm: int = SLOPE_CONFIRM,
) -> pd.DataFrame:
    df = df.copy()
    low_n = df["l"].rolling(k, min_periods=k).min()
    high_n = df["h"].rolling(k, min_periods=k).max()
    rng = (high_n - low_n).replace(0, np.nan)
    df["fastK"] = 100.0 * (df["c"] - low_n) / rng
    df["slowD"] = df["fastK"].rolling(d, min_periods=d).mean()
    d_rising = df["slowD"] > df["slowD"].shift(1)
    d_falling = df["slowD"] < df["slowD"].shift(1)
    if slope_confirm == 2:
        df["uptrend"] = d_rising & d_rising.shift(1).fillna(False)
        df["downtrend"] = d_falling & d_falling.shift(1).fillna(False)
    elif slope_confirm == 1:
        df["uptrend"] = d_rising
        df["downtrend"] = d_falling
    else:
        raise ValueError(f"bad slope_confirm {slope_confirm}")
    osc = B.ema(df["c"], fast) - B.ema(df["c"], slow)
    df["osc310"] = osc
    df["osc310_sig"] = B.ema(osc, sig)
    hi2 = df["h"].shift(1).rolling(2, min_periods=2).max()
    lo2 = df["l"].shift(1).rolling(2, min_periods=2).min()
    df["inside2"] = (df["h"] < hi2) & (df["l"] > lo2)
    df["hook_dn"] = B.crossed_below(df["fastK"], df["slowD"])
    df["hook_up"] = B.crossed_above(df["fastK"], df["slowD"])
    return df
