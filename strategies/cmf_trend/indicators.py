"""Marc Chaikin's Chaikin Money Flow (CMF) indicators.

CMF measures money-flow volume over a 21-bar window:

    CLV = ((C - L) - (H - C)) / (H - L)     # close location value
    MFV = CLV * V                            # money flow volume
    CMF = sum(MFV, 21) / sum(V, 21)

Positive CMF = accumulation (closes in the upper half of the range);
negative = distribution. Crosses of the zero line mark shifts in buying
vs selling pressure. A 200-bar SMA regime filter keeps trades with the
price trend. All causal: only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 21  # Chaikin's standard CMF window
REGIME = 200  # price-trend regime filter


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    rng = (h - l).replace(0, float("nan"))
    clv = ((c - l) - (h - c)) / rng
    clv = clv.fillna(0.0)  # flat bar: no location information
    mfv = clv * v
    df["cmf"] = mfv.rolling(N, min_periods=N).sum() / v.rolling(
        N, min_periods=N
    ).sum().replace(0, float("nan"))
    df["cmf_regime"] = B.sma(c, REGIME)
    return df
