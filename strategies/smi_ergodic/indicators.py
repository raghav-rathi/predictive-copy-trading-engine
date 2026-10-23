"""William Blau's SMI Ergodic Oscillator.

    m     = c.diff()
    smi   = 100 * EMA(EMA(m, 5), 20) / EMA(EMA(abs(m), 5), 20)
    signal = EMA(smi, 5)

Blau's SMI Ergodic ("Momentum, Direction, and Divergence", 1995) is
the same double-smoothed ergodic lineage as the True Strength Index:
an exponentially smoothed ratio of double-smoothed momentum to
double-smoothed absolute momentum. The TSI ships with slower 25/13
parameters; the SMI Ergodic uses Blau's faster 5/20 ergodic pair and
a 5-bar signal line, oscillating in a bounded [-100, +100] band with
overbought/oversold zones at +/-40. Being a ratio of the momentum to
its own magnitude, the oscillator is exactly scale-invariant — a
10-point-per-bar grind and a 1000-point-per-bar grind read the same.

Columns:

    smi         -- SMI Ergodic oscillator (percent, bounded +/-100)
    smi_signal  -- 5-bar EMA of smi (the trigger/signal line)
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: the EMAs at bar j use data through bar j only
(min_periods=n via B.ema). Division by zero (flat series, momentum
= 0) is guarded to 0, not NaN — the warmup NaN band from the
double smoothing is preserved.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ERGO_FAST = 5   # inner ergodic smoothing (Blau's SMI Ergodic, fixed a priori)
ERGO_SLOW = 20  # outer ergodic smoothing (Blau's SMI Ergodic, fixed a priori)
SIGNAL_N = 5    # signal-line smoothing (Blau's SMI Ergodic, fixed a priori)
ZONE = 40.0     # overbought / oversold zones (Blau's SMI Ergodic, fixed a priori)


def smi_ergodic(m: pd.Series, fast: int = ERGO_FAST,
                slow: int = ERGO_SLOW) -> pd.Series:
    """Blau's SMI Ergodic of the momentum series ``m``.

    100 * EMA(EMA(m, fast), slow) / EMA(EMA(|m|, fast), slow).
    Bounded in [-100, +100] (|ema(m)| <= ema(|m|)); flat-momentum
    bars (denominator == 0) yield 0; the warmup band stays NaN.
    """
    num = B.ema(B.ema(m, fast), slow)
    den = B.ema(B.ema(m.abs(), fast), slow)
    ratio = 100.0 * num / den.where(den != 0.0)
    return ratio.mask(den == 0.0, 0.0).rename("smi")


def add_indicators(df: pd.DataFrame, fast: int = ERGO_FAST,
                   slow: int = ERGO_SLOW,
                   signal_n: int = SIGNAL_N) -> pd.DataFrame:
    df = df.copy()
    df["smi"] = smi_ergodic(df["c"].diff(), fast, slow)
    df["smi_signal"] = B.ema(df["smi"], signal_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
