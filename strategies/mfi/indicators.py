"""Money Flow Index indicators (Gene Quong & Avrum Soudack, 1989).

The volume-weighted RSI: typical price TP = (H+L+C)/3, raw money flow =
TP * volume. Positive flow sums flow on bars where TP rises, negative
flow where TP falls:

    MR = sum(positive flow, MFI_LEN) / sum(negative flow, MFI_LEN)
    MFI = 100 - 100 / (1 + MR)

Classic length 14. A zero negative-flow window (all up bars) yields
MFI = 100 (defined limit, handled explicitly); a fully flat window gives
NaN -- no fake signal. No lookahead: every bar uses only data through
that bar's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MFI_LEN = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    mf = tp * df["v"]
    tp_chg = tp.diff()
    pos = mf.where(tp_chg > 0, 0.0).rolling(MFI_LEN, min_periods=MFI_LEN).sum()
    neg = mf.where(tp_chg < 0, 0.0).rolling(MFI_LEN, min_periods=MFI_LEN).sum()
    mr = pos / neg.replace(0, np.nan)
    mfi = 100.0 - 100.0 / (1.0 + mr)
    # All-up window (neg == 0, pos > 0): the limit is 100, not NaN.
    all_up = (neg == 0) & (pos > 0)
    mfi = mfi.where(~all_up, 100.0)
    df["mfi"] = mfi
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
