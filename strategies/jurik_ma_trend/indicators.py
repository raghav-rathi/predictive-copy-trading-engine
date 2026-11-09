"""Jurik Moving Average (JMA) indicators.

Public three-stage reconstruction of Mark Jurik's proprietary JMA
(the original algorithm was never published). This implementation
follows the widely-circulated reconstruction documented at
https://docs.wickra.org/Indicators/Indicator-Jma and in the
three-stage form in "Jurik JMA Algorithm Revealed — The 3 Stages of
Jurik Smoothing" (https://forex-station.com/attach/file/3413178),
which is also the form used by pandas-ta and the TradingView Pine
``jma`` libraries (reconstruction by Igor Durkin, MQL4 port by
Nikolay Kositsin):

    beta        = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha       = beta ** power
    phase_ratio = clamp(phase / 100 + 1.5, 0.5, 2.5)

    Stage 1 (adaptive EMA):
        e0_t = (1 - alpha) * price_t + alpha * e0_{t-1}
    Stage 2 (Kalman-style detrender, phase-weighted):
        e1_t = (price_t - e0_t) * (1 - beta) + beta * e1_{t-1}
        ma2_t = e0_t + phase_ratio * e1_t
    Stage 3 (Jurik adaptive filter):
        e2_t = (ma2_t - JMA_{t-1}) * (1 - alpha)**2 + alpha**2 * e2_{t-1}
        JMA_t = JMA_{t-1} + e2_t

State is seeded with e0 = JMA = first close and e1 = e2 = 0, so JMA
emits from the first bar. The recursion only ever uses data through
bar i's close, so there is no lookahead. Shipped parameters:
length 14, phase 50 (phase_ratio 2.0), power 2.
"""

import numpy as np
import pandas as pd

JMA_LENGTH = 14
JMA_PHASE = 50.0
JMA_POWER = 2

INDICATOR_COLS = [
    "jma",
    "jma_rising",
]


def _jma_values(closes: np.ndarray, length: int, phase: float, power: int) -> np.ndarray:
    n = len(closes)
    out = np.full(n, np.nan)
    if n == 0:
        return out
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta ** power
    phase_ratio = min(max(phase / 100.0 + 1.5, 0.5), 2.5)
    e0 = float(closes[0])
    e1 = 0.0
    e2 = 0.0
    jma = float(closes[0])
    out[0] = jma
    for i in range(1, n):
        price = float(closes[i])
        e0 = (1.0 - alpha) * price + alpha * e0
        e1 = (price - e0) * (1.0 - beta) + beta * e1
        ma2 = e0 + phase_ratio * e1
        e2 = (ma2 - jma) * (1.0 - alpha) ** 2 + alpha ** 2 * e2
        jma = jma + e2
        out[i] = jma
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["jma"] = _jma_values(
        df["c"].to_numpy(dtype=float), JMA_LENGTH, JMA_PHASE, JMA_POWER
    )
    df["jma_rising"] = (df["jma"] > df["jma"].shift(1)).fillna(False)
    return df
