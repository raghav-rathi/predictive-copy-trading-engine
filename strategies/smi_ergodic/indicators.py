"""William Blau's SMI Ergodic Oscillator indicators.

Blau ("Momentum, Direction, and Divergence", 1995) defines the ergodic
oscillator as double-smoothed momentum normalized by double-smoothed
absolute momentum:

    SMI = 100 * EMA(EMA(d, r), s) / EMA(EMA(|d|, r), s),  d = C - C[1]

The "SMI Ergodic" packaging adds a signal line (EMA of SMI) for trigger
crosses. The double smoothing makes it bounded and less whipsaw-prone
than raw momentum; the zero line marks the momentum regime. All causal:
only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

R = 20  # first smoothing stage (Blau varied this freely by market)
S = 5  # second smoothing stage
SIG = 5  # signal-line EMA


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["c"].diff()
    num = B.ema(B.ema(d, R), S)
    den = B.ema(B.ema(d.abs(), R), S)
    df["smi"] = 100.0 * num / den.replace(0, float("nan"))
    df["smi_signal"] = B.ema(df["smi"], SIG)
    return df
