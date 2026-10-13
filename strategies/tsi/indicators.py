"""True Strength Index (William Blau, 1991).

m = close - prev close
TSI = 100 * EMA(EMA(m, r), s) / EMA(EMA(|m|, r), s)
signal = EMA(TSI, sig)

Blau's published defaults: r=25, s=13, sig=7. Pure pandas; no lookahead
(EMA with min_periods, all through bar i).
"""

import numpy as np
import pandas as pd

from strategies import base as B

R = 25
S = 13
SIG = 7


def add_indicators(
    df: pd.DataFrame, r: int = R, s: int = S, sig: int = SIG
) -> pd.DataFrame:
    df = df.copy()
    m = df["c"].diff()
    am = m.abs()
    dbl_m = B.ema(B.ema(m, r), s)
    dbl_am = B.ema(B.ema(am, r), s)
    denom = dbl_am.replace(0, np.nan)
    df["tsi"] = 100.0 * dbl_m / denom
    df["tsi_signal"] = B.ema(df["tsi"], sig)
    return df
