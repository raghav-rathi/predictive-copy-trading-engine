"""Altman Relative Momentum Index, RMI(20, 5).

The only difference from Wilder RSI: the momentum term is
C[i] - C[i-5] instead of C[i] - C[i-1]. Gains and losses of that
5-bar change are Wilder-smoothed over 20 bars and rescaled to
0-100. RMI(14, 1) reduces exactly to RSI(14) — that identity is
asserted in the unit tests. Columns: rmi, atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def rmi_series(c: pd.Series, n: int = 20, m: int = 5) -> pd.Series:
    mom = c - c.shift(m)
    gain = mom.clip(lower=0)
    loss = -mom.clip(upper=0)
    ag = gain.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    al = loss.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = ag / al.replace(0, float("nan"))
    out = 100 - 100 / (1 + rs)
    return out.fillna(100.0 * (ag > 0).astype(float))


def add_indicators(df: pd.DataFrame, n: int = 20, m: int = 5) -> pd.DataFrame:
    df = df.copy()
    df["rmi"] = rmi_series(df["c"], n, m)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
