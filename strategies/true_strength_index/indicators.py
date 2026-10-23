"""William Blau's True Strength Index (TSI), Stocks & Commodities 1991.

Double-smoothed momentum oscillator:

    m[j]      = c[j] - c[j-1]
    num[j]    = EMA(EMA(m, 25), 13)[j]
    den[j]    = EMA(EMA(|m|, 25), 13)[j]
    TSI[j]    = 100 * num[j] / den[j]     (0 where den == 0)
    signal[j] = EMA(TSI, 7)[j]

Blau's construction smooths raw price momentum twice (the
"double-smoothed" part), suppressing the whipsaw that a single EMA of
momentum still shows, then normalizes by the double-smoothed absolute
momentum so the oscillator is bounded in [-100, +100]. The signal line
is a further EMA(7) of the TSI.

All EMAs use pandas ewm(span=n, adjust=False, min_periods=n) via
strategies.base.ema. No lookahead: every value at bar j uses data
through bar j only (min_periods -> leading NaN warmup). A flat market
(den == 0) yields TSI == 0 rather than NaN/inf.

Columns:

    tsi        -- double-smoothed momentum, [-100, 100]
    tsi_signal -- EMA(7) of TSI
"""

import pandas as pd

from strategies import base as B

LONG_SMOOTH = 25    # first (slow) smoothing of momentum
SHORT_SMOOTH = 13   # second (fast) smoothing
SIGNAL_N = 7        # signal-line EMA length


def true_strength_index(c: pd.Series, r: int = LONG_SMOOTH,
                        s: int = SHORT_SMOOTH) -> pd.Series:
    """TSI of the close series: 100 * EMA(EMA(diff, r), s) / EMA(EMA(|diff|, r), s).

    Denominator 0 (perfectly flat market) maps to TSI 0; NaN warmup from
    min_periods is preserved.
    """
    m = c.diff()
    num = B.ema(B.ema(m, r), s)
    den = B.ema(B.ema(m.abs(), r), s)
    out = (100.0 * num / den).rename("tsi")
    return out.where((den != 0) | den.isna(), 0.0)


def add_indicators(df: pd.DataFrame, r: int = LONG_SMOOTH,
                   s: int = SHORT_SMOOTH, sig_n: int = SIGNAL_N) -> pd.DataFrame:
    df = df.copy()
    df["tsi"] = true_strength_index(df["c"], r, s)
    df["tsi_signal"] = B.ema(df["tsi"], sig_n)
    return df
