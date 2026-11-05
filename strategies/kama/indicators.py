"""Kaufman's Adaptive Moving Average KAMA(10,2,30) indicators."""

import numpy as np
import pandas as pd

INDICATOR_COLS = ["kama"]


def kama_series(c: pd.Series, n: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    """Kaufman's Adaptive Moving Average.

    ER = |close - close n ago| / sum(|close - prior close|) over n bars.
    SC = [ER * (2/(fast+1) - 2/(slow+1)) + 2/(slow+1)]^2.
    KAMA = prev KAMA + SC * (close - prev KAMA).
    """
    close = c.to_numpy(dtype=float)
    m = len(close)
    out = np.full(m, np.nan)
    if m == 0:
        return pd.Series(out, index=c.index, name="kama")
    diff = np.abs(np.diff(close, prepend=np.nan))
    # sum of |daily changes| over n bars, aligned to bar i
    change_sum = pd.Series(diff).rolling(n, min_periods=n).sum().to_numpy()
    direction = np.abs(close - np.concatenate([np.full(n, np.nan), close[:-n]])) if m > n else np.full(m, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        er = direction / change_sum
    fast_sc = 2.0 / (fast + 1)
    slow_sc = 2.0 / (slow + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    # Seed KAMA at the first bar where ER is defined; before that track price.
    first = int(np.where(np.isfinite(sc))[0][0]) if np.isfinite(sc).any() else None
    if first is None:
        return pd.Series(close.copy(), index=c.index, name="kama")
    out[: first + 1] = close[: first + 1]
    prev = close[first]
    out[first] = prev
    for i in range(first + 1, m):
        s = sc[i]
        if not np.isfinite(s):
            s = slow_sc ** 2
        prev = prev + s * (close[i] - prev)
        out[i] = prev
    return pd.Series(out, index=c.index, name="kama")


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    from strategies import base as B

    df = df.copy()
    df["kama"] = kama_series(df["c"], 10, 2, 30)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
