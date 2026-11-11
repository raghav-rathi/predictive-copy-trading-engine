"""Vortex Indicator crossover gated by a Bollinger BandWidth squeeze.

Vortex (Botes & Siepman, TASC Jan 2010) -- same VI+/VI- formulas as
strategies/vortex:

    VM+  = |h - l.shift(1)|
    VM-  = |l - h.shift(1)|
    VI+  = sum_14(VM+) / sum_14(TR)    (VI- likewise)

BandWidth(20, 2) = (upper - lower) / middle, from Bollinger Bands.
Squeeze = BandWidth below its own 120-bar 20th percentile (a
volatility-compression regime). The squeeze gate is open while the
squeeze is true OR within 5 bars after it ends, so a cross that fires
on the expansion out of the squeeze still counts.

Columns:

    vi_pos / vi_neg   -- VI+(14) / VI-(14)
    vi_spread         -- vi_pos - vi_neg
    bb_bandwidth      -- (bb_upper - bb_lower) / bb_mid
    bb_bandwidth_p20  -- 120-bar 20th percentile of bb_bandwidth
    squeeze           -- bb_bandwidth < bb_bandwidth_p20
    squeeze_recent    -- squeeze true on this bar or any of the
                         previous 5 bars
    atr               -- Wilder ATR(14) for the risk layer

No lookahead: every rolling value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

VORTEX_N = 14
BB_N = 20
BB_K = 2.0
SQUEEZE_WINDOW = 120
SQUEEZE_PCT = 0.20
SQUEEZE_RECENT_BARS = 5

INDICATOR_COLS = [
    "vi_pos",
    "vi_neg",
    "vi_spread",
    "bb_bandwidth",
    "bb_bandwidth_p20",
    "squeeze",
    "squeeze_recent",
    "atr",
]


def vortex(h: pd.Series, l: pd.Series, c: pd.Series, n: int = VORTEX_N) -> pd.DataFrame:
    """Return vi_pos / vi_neg for the Vortex Indicator with window n."""
    vm_pos = (h - l.shift(1)).abs()
    vm_neg = (l - h.shift(1)).abs()
    tr = B.true_range(h, l, c)
    sum_pos = vm_pos.rolling(n, min_periods=n).sum()
    sum_neg = vm_neg.rolling(n, min_periods=n).sum()
    sum_tr = tr.rolling(n, min_periods=n).sum()
    safe = sum_tr.replace(0.0, np.nan)
    vi_pos = sum_pos / safe
    vi_neg = sum_neg / safe
    return pd.DataFrame({"vi_pos": vi_pos, "vi_neg": vi_neg})


def add_indicators(df: pd.DataFrame, n: int = VORTEX_N) -> pd.DataFrame:
    df = df.copy()
    v = vortex(df["h"], df["l"], df["c"], n)
    df["vi_pos"] = v["vi_pos"]
    df["vi_neg"] = v["vi_neg"]
    df["vi_spread"] = v["vi_pos"] - v["vi_neg"]
    bb = B.bollinger(df["c"], BB_N, BB_K)
    df["bb_bandwidth"] = (bb["bb_upper"] - bb["bb_lower"]) / bb["bb_mid"]
    df["bb_bandwidth_p20"] = df["bb_bandwidth"].rolling(
        SQUEEZE_WINDOW, min_periods=SQUEEZE_WINDOW).quantile(SQUEEZE_PCT)
    df["squeeze"] = (df["bb_bandwidth"] < df["bb_bandwidth_p20"]).fillna(False)
    # Gate open while squeezing or within 5 bars after the squeeze ends:
    # a 6-bar rolling max covers the current bar + the previous 5.
    df["squeeze_recent"] = (
        df["squeeze"].rolling(SQUEEZE_RECENT_BARS + 1, min_periods=1).max() > 0
    )
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
