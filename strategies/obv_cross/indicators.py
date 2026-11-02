"""On-Balance Volume cross indicators (Joseph Granville).

OBV adds the bar's volume on up closes, subtracts it on down
closes, and is unchanged on flat closes. The traded line is
OBV against its own EMA(20): volume flow leading price is the
thesis — OBV turning before price is the confirmation.

Columns:
    obv, obv_ema, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["c"].diff().to_numpy()
    direction = np.where(d > 0, 1.0, np.where(d < 0, -1.0, 0.0))
    obv = pd.Series(np.cumsum(direction * df["v"].to_numpy()), index=df.index)
    df["obv"] = obv
    df["obv_ema"] = B.ema(obv, 20)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
