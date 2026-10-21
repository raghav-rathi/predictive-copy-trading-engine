"""TRIX -- triple-smoothed exponential momentum (Jack Hutson, early 1980s).

    EMA1   = EMA(close, len)
    EMA2   = EMA(EMA1, len)
    EMA3   = EMA(EMA2, len)
    trix   = 100 * (EMA3 - EMA3.shift(1)) / EMA3.shift(1)
    signal = EMA(trix, sig_n)

The triple smoothing kills whipsaw: TRIX only moves when the smoothed
price path itself turns, so crosses against its own signal line mark
confirmed momentum turns rather than one-bar noise. Columns:

    trix        -- TRIX(len)
    trix_signal -- EMA(trix, sig_n)
    ema3        -- the triple-smoothed close itself
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every EMA on bar j uses data through bar j only;
ewm(min_periods=len) means EMA3's first fully-formed value arrives
after ~3*(len-1) bars, and the signal line after another sig_n-1.
"""

import numpy as np
import pandas as pd

from strategies import base as B

TRIX_LEN = 14   # shipped default
SIGNAL_N = 9    # shipped default


def trix(c: pd.Series, n: int = TRIX_LEN, sig_n: int = SIGNAL_N) -> pd.DataFrame:
    """TRIX oscillator and its signal line from the close series."""
    ema1 = B.ema(c, n)
    ema2 = B.ema(ema1, n)
    ema3 = B.ema(ema2, n)
    prev = ema3.shift(1)
    raw = 100.0 * (ema3 - prev) / prev.replace(0.0, np.nan)
    sig = B.ema(raw, sig_n)
    return pd.DataFrame({"ema3": ema3, "trix": raw, "trix_signal": sig})


def add_indicators(df: pd.DataFrame, n: int = TRIX_LEN,
                   sig_n: int = SIGNAL_N) -> pd.DataFrame:
    df = df.copy()
    t = trix(df["c"], n, sig_n)
    df["trix"] = t["trix"]
    df["trix_signal"] = t["trix_signal"]
    df["ema3"] = t["ema3"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
