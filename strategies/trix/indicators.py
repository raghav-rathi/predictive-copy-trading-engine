"""TRIX momentum indicators (triple-smoothed exponential average).

TRIX(n): e1 = EMA(close, n); e2 = EMA(e1, n); e3 = EMA(e2, n);
         TRIX = 100 * (e3 - e3[1]) / e3[1]   (1-bar % change of the
         triple-smoothed series). The triple smoothing filters out
         insignificant cycles; the result is a momentum oscillator that
         leads price turns. Classic n=15 with a 9-bar SMA signal line.
All causal: only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

N = 15      # classic TRIX period
SIGNAL = 9  # signal-line smoothing


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    e3 = B.ema(B.ema(B.ema(df["c"], N), N), N)
    trix = 100.0 * (e3 - e3.shift(1)) / e3.shift(1).replace(0, float("nan"))
    df["trix"] = trix
    df["trix_signal"] = trix.rolling(SIGNAL, min_periods=SIGNAL).mean()
    df["trix_minus_signal"] = trix - df["trix_signal"]
    return df
