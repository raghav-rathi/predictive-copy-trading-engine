"""Schwager volatility ratio (VR).

VR = true range / EMA of the *prior* true ranges (the current bar is
excluded from the EMA, so a wide bar cannot dilute its own reading).
VR > 2.0 marks a wide-ranging bar -- a bar whose range is more than
twice its recent norm.

    vr       -- true range / EMA(TR, 14) of prior bars
    bar_pos  -- close position inside the bar: 0 = low, 1 = high
    ret5     -- 5-bar close return (trend context for the wide bar)
    atr      -- Wilder ATR(14) for the risk layer

No lookahead: VR on bar i uses true ranges through bar i and the EMA
of ranges through bar i-1 only.

Source: Schwager Volatility Ratio --
https://www.incrediblecharts.com/indicators/volatility_ratio_schwager.php
"""

import numpy as np
import pandas as pd

from strategies import base as B

VR_EMA_N = 14  # shipped default: EMA length for the true-range norm


def add_indicators(df: pd.DataFrame, vr_ema_n: int = VR_EMA_N) -> pd.DataFrame:
    df = df.copy()
    tr = B.true_range(df["h"], df["l"], df["c"])
    # EMA of prior true ranges only: shift first, then EMA.
    ema_prior = tr.shift(1).ewm(
        span=vr_ema_n, adjust=False, min_periods=vr_ema_n).mean()
    df["vr"] = tr / ema_prior
    rng = (df["h"] - df["l"]).replace(0, np.nan)
    df["bar_pos"] = (df["c"] - df["l"]) / rng
    df["ret5"] = df["c"] / df["c"].shift(5) - 1
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
