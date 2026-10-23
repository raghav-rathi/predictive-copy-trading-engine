"""Rolling 24-bar VWAP indicators (session-less, for 24/7 crypto).

Classic VWAP anchors to the session open; crypto has no sessions, so
this strategy uses a trailing 24-bar (1-day on 1h bars) VWAP instead:

    tp        = (h + l + c) / 3
    vwap[j]   = sum(tp*v over j-23..j) / sum(v over j-23..j)

Zero-volume guard: if the rolling volume sum is zero the division
would explode, so the series falls back to the typical price (which
is what VWAP means when there is no volume to weight by). Any NaN
is forward-filled then back-filled so the warmup is the only NaN
region.

    vwap_slope[j] = vwap[j] - vwap[j-3]   (is the benchmark rising?)
    vol_ratio[j]  = v[j] / SMA(v, 20)     (is the bar on strong flow?)

Columns:

    vwap       -- 24-bar rolling VWAP of typical price
    vwap_slope -- vwap minus vwap 3 bars ago
    vol_ratio  -- volume / 20-bar simple mean volume
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n).
"""

import numpy as np
import pandas as pd

from strategies import base as B

VWAP_N = 24       # shipped default (fixed a priori)
SLOPE_N = 3       # slope lookback
VOL_N = 20        # volume moving-average length


def rolling_vwap(tp: pd.Series, v: pd.Series, n: int = VWAP_N) -> pd.Series:
    """Trailing VWAP of typical price; falls back to tp when volume is zero."""
    tpv = tp * v
    num = tpv.rolling(n, min_periods=n).sum()
    den = v.rolling(n, min_periods=n).sum()
    vwap = (num / den).where(den != 0)
    # Zero-volume guard: no volume to weight by -> VWAP = typical price.
    vwap = vwap.where(den != 0, tp)
    return vwap.rename("vwap")


def add_indicators(df: pd.DataFrame, n: int = VWAP_N,
                   slope_n: int = SLOPE_N,
                   vol_n: int = VOL_N) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    vwap = rolling_vwap(tp, df["v"], n)
    df["vwap"] = vwap.ffill().bfill()
    df["vwap_slope"] = (df["vwap"] - df["vwap"].shift(slope_n)).bfill().fillna(0.0)
    sma_vol = df["v"].rolling(vol_n, min_periods=vol_n).mean()
    df["vol_ratio"] = (df["v"] / sma_vol).where(sma_vol != 0)
    df["vol_ratio"] = df["vol_ratio"].replace([np.inf, -np.inf], np.nan)
    df["vol_ratio"] = df["vol_ratio"].ffill().bfill().fillna(1.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
