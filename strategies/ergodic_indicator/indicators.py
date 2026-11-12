"""William Blau's ergodic oscillator / True Strength Index
(Momentum, Direction, and Divergence, 1995; TSI first published in
Technical Analysis of Stocks & Commodities, Nov 1991).

Blau's double-smoothing construction on one-bar momentum:

    m[j]       = c[j] - c[j-1]
    PC[j]      = EMA(EMA(m, 25), 13)[j]
    APC[j]     = EMA(EMA(|m|, 25), 13)[j]
    ergodic[j] = 100 * PC[j] / APC[j]      (0 where APC == 0)
    signal[j]  = EMA(ergodic, 7)[j]

The oscillator is bounded in [-100, +100] because the denominator
(double-smoothed absolute momentum) is never smaller than the absolute
value of the numerator. Blau's published defaults are r = 25, s = 13,
signal 7 -- the same lengths the repo's true_strength_index strategy
uses; the two strategies differ in the signal rule, not the
oscillator (see CALIBRATION.md).

All EMAs use pandas ewm(span=n, adjust=False, min_periods=n) via
strategies.base.ema. No lookahead: every value at bar j uses data
through bar j only (min_periods -> leading NaN warmup). A flat market
(APC == 0) yields ergodic == 0 rather than NaN/inf.

Columns: ergodic, ergodic_signal, atr.
"""

import pandas as pd

from strategies import base as B

LONG_SMOOTH = 25    # first (slow) smoothing of momentum
SHORT_SMOOTH = 13   # second (fast) smoothing
SIGNAL_N = 7        # signal-line EMA length

INDICATOR_COLS = ["ergodic", "ergodic_signal", "atr"]


def ergodic_oscillator(c: pd.Series, r: int = LONG_SMOOTH,
                       s: int = SHORT_SMOOTH) -> pd.Series:
    """Ergodic oscillator: 100 * EMA(EMA(diff, r), s) / EMA(EMA(|diff|, r), s).

    Denominator 0 (perfectly flat market) maps to 0; NaN warmup from
    min_periods is preserved.
    """
    m = c.diff()
    num = B.ema(B.ema(m, r), s)
    den = B.ema(B.ema(m.abs(), r), s)
    out = (100.0 * num / den).rename("ergodic")
    return out.where((den != 0) | den.isna(), 0.0)


def add_indicators(df: pd.DataFrame, r: int = LONG_SMOOTH,
                   s: int = SHORT_SMOOTH, sig_n: int = SIGNAL_N) -> pd.DataFrame:
    df = df.copy()
    df["ergodic"] = ergodic_oscillator(df["c"], r, s)
    df["ergodic_signal"] = B.ema(df["ergodic"], sig_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
