"""ROC(12) momentum — rate of change of close vs 12 bars ago.

Columns: roc, atr. No lookahead: ROC uses only closes through bar i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 12


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["roc"] = (df["c"] / df["c"].shift(PERIOD) - 1.0) * 100.0
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
