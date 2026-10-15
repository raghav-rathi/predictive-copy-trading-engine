"""Tillson T3 indicators (Tim Tillson, 1998).

T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3, where e1..e6 are six chained EMAs
of the source and, with volume factor a:
  c1 = -a^3
  c2 =  3a^2 + 3a^3
  c3 = -6a^2 - 3a - 3a^3
  c4 =  1 + 3a + a^3 + 3a^2        (a = 0.7 default)

A low-lag smoother built as a weighted sum of single-through-sextuple
EMAs. The traded system is the fast/slow T3 cross. No lookahead: every
value on bar i uses bars through i only.
"""

import pandas as pd

from strategies import base as B

FAST_N = 5
SLOW_N = 15
VFACTOR = 0.7


def _t3(s: pd.Series, n: int, vf: float = VFACTOR) -> pd.Series:
    e1 = B.ema(s, n)
    e2 = B.ema(e1, n)
    e3 = B.ema(e2, n)
    e4 = B.ema(e3, n)
    e5 = B.ema(e4, n)
    e6 = B.ema(e5, n)
    c1 = -(vf**3)
    c2 = 3 * vf**2 + 3 * vf**3
    c3 = -6 * vf**2 - 3 * vf - 3 * vf**3
    c4 = 1 + 3 * vf + vf**3 + 3 * vf**2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["t3_fast"] = _t3(df["c"], FAST_N)
    df["t3_slow"] = _t3(df["c"], SLOW_N)
    return df
