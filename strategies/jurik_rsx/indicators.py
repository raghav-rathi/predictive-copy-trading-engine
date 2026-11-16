"""Jurik RSX — RSI on Jurik's three-stage smoothing cascade.

RECONSTRUCTION, not Jurik's exact code: Jurik Research's RSX/JMA
internals are proprietary. What is implemented here is the widely
ported public reconstruction of the RSX, as documented by Wickra
(from ``crates/wickra-core/src/indicators/rsx.rs``):

    f18 = 3 / (length + 2),  f20 = 1 - f18
    stage(a, b, in):  a = f20*a + f18*in;  b = f18*a + f20*b
                      out = 1.5*a - 0.5*b
    change = price - prev_price
    v14 = stage3(change)          # signed change, three cascaded stages
    v1C = stage3(|change|)        # absolute change, three cascaded stages
    RSX = clamp((v14 / v1C + 1) * 50, 0, 100)   # 50 when v1C == 0

Each stage is a "double-EMA with overshoot" (1.5*a - 0.5*b), the same
lag-cancelling structure as a DEMA. Running both the signed move and
its magnitude through three such stages and forming the RSI-style
ratio yields an oscillator that follows the RSI but is dramatically
smoother for the same length. A flat market returns the neutral 50.

    rsx  -- Jurik RSX, [0, 100], neutral 50
    atr  -- Wilder ATR(14) for the risk layer

Warmup: the cascade needs length + 1 inputs before its first
emission (15 bars at length 14); the strategy warmup is 45 bars to
let the recursive cascade settle (see the Wickra docs' warning
about warmup transients). No lookahead: RSX on bar j uses closes
through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LENGTH = 14  # shipped default
CROSS_LEVEL = 50.0
EXTREME_HIGH = 80.0
EXTREME_LOW = 20.0


def _stage_cascade(x: np.ndarray, length: int) -> np.ndarray:
    """Run a series through three cascaded double-EMA stages."""
    f18 = 3.0 / (length + 2.0)
    f20 = 1.0 - f18
    a1 = b1 = a2 = b2 = a3 = b3 = 0.0
    out = np.empty(len(x), dtype=float)
    for i, v in enumerate(x):
        a1 = f20 * a1 + f18 * v
        b1 = f18 * a1 + f20 * b1
        o1 = 1.5 * a1 - 0.5 * b1
        a2 = f20 * a2 + f18 * o1
        b2 = f18 * a2 + f20 * b2
        o2 = 1.5 * a2 - 0.5 * b2
        a3 = f20 * a3 + f18 * o2
        b3 = f18 * a3 + f20 * b3
        out[i] = 1.5 * a3 - 0.5 * b3
    return out


def rsx(c: pd.Series, length: int = LENGTH) -> pd.Series:
    """Jurik RSX (public reconstruction) of a price series."""
    change = c.diff().fillna(0.0).to_numpy(dtype=float)
    v14 = _stage_cascade(change, length)
    v1c = _stage_cascade(np.abs(change), length)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(v1c == 0.0, 0.0, v14 / v1c)
    out = np.clip((ratio + 1.0) * 50.0, 0.0, 100.0)
    s = pd.Series(out, index=c.index, dtype=float)
    # First emission after length + 1 inputs (index `length`).
    s.iloc[:length] = np.nan
    return s


def add_indicators(df: pd.DataFrame, length: int = LENGTH) -> pd.DataFrame:
    df = df.copy()
    df["rsx"] = rsx(df["c"], length)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
