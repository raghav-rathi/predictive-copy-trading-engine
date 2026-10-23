"""RSI divergence indicators.

Plain-English idea: momentum usually confirms price. When price makes
a new low but RSI refuses to (a higher RSI low while oversold), sellers
are exhausting themselves — the same in reverse at tops. The entry is
not taken on the divergence alone but on RSI crossing back through
30/70 afterwards, which confirms momentum has actually turned.

Mechanics:
  rsi      = Wilder RSI(14)
  pivots   = 5-bar fractals on close and on RSI, confirmed causally
             (a pivot centred at bar j is usable from bar j+5)

The divergence scan itself lives in signals.py. No lookahead: RSI is
Wilder-smoothed left-to-right and pivots carry the 5-bar confirmation
lag.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_LEN = 14
PIVOT_K = 5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], RSI_LEN)
    return df
