"""Money Flow Index MFI(14) by Gene Quong and Avrum Soudack.

    Typical price  = (h + l + c) / 3
    Raw money flow = typical price * volume
    Positive flow  = raw money flow on bars where the typical
                     price rose vs the prior bar
    Negative flow  = raw money flow on bars where the typical
                     price fell vs the prior bar (summed as a
                     positive magnitude)
    Money flow ratio = sum(positive flow, 14) / sum(negative flow, 14)
    MFI = 100 - 100 / (1 + money flow ratio)

Edge cases: a bar with an unchanged typical price contributes
to neither sum. If the 14-bar negative sum is 0 and the
positive sum is > 0, MFI = 100 (all money flowing in); if
both sums are 0 (flat window), MFI = 50 (neutral). First
valid value at bar 13 (14 bars, min_periods=14); earlier
bars are NaN.

Columns:
    mfi -- Money Flow Index(14), 0-100
    atr -- Wilder ATR(14) for the risk layer

Causal: each value uses only bars through the current close.
Note on volume: on Hyperliquid the v column is base-asset
volume per bar; MFI here is a volume-weighted momentum
reading on that venue's flow, not whole-market dollar volume.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    raw = tp * df["v"]
    d = tp.diff()
    pos = raw.where(d > 0, 0.0)
    neg = raw.where(d < 0, 0.0)
    pos_sum = pos.rolling(PERIOD, min_periods=PERIOD).sum()
    neg_sum = neg.rolling(PERIOD, min_periods=PERIOD).sum()
    ratio = pos_sum / neg_sum.replace(0, np.nan)
    mfi = 100.0 - 100.0 / (1.0 + ratio)
    # All-inflow window (neg_sum == 0, pos_sum > 0) -> 100;
    # flat window (both sums 0) -> 50 neutral.
    mfi = mfi.where(
        ~((neg_sum == 0) & (pos_sum > 0)), 100.0
    ).where(~((neg_sum == 0) & (pos_sum == 0)), 50.0)
    df["mfi"] = mfi
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
