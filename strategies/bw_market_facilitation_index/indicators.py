"""Bill Williams Market Facilitation Index (BW MFI) indicators.

BW MFI_t = (high_t - low_t) / volume_t, from Bill Williams,
"Trading Chaos" (Wiley, 1995). Only bar-to-bar CHANGE matters — the
absolute level is scale-dependent (it mixes price units and volume
units), so each bar is classified against the previous bar:

  GREEN = MFI up and volume up
  FADE  = MFI down and volume down
  FAKE  = MFI up and volume down
  SQUAT = MFI down and volume up  (heavy volume, little range — a
          battle that often precedes a breakout)

Volume == 0 is guarded to MFI = 0 (no division by zero). The first
bar has no previous bar, so its type is "none". A bar whose MFI (or
volume) is exactly unchanged vs the previous bar counts as "down"
(not up) — the classification uses strict > for "up".

All computation is causal: bar i uses only data through bar i.
"""

import numpy as np
import pandas as pd

from strategies.base import ema

EMA_PERIOD = 20

INDICATOR_COLS = [
    "bw_mfi",
    "bar_type",
    "ema20",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = df["h"] - df["l"]
    vol = df["v"].to_numpy(dtype=float)
    mfi = np.divide(
        rng.to_numpy(dtype=float),
        vol,
        out=np.zeros(len(df), dtype=float),
        where=vol != 0,
    )
    df["bw_mfi"] = mfi

    mfi_s = pd.Series(mfi, index=df.index)
    mfi_up = (mfi_s > mfi_s.shift(1)).to_numpy()
    vol_up = (df["v"] > df["v"].shift(1)).to_numpy()

    bar_type = np.full(len(df), "none", dtype=object)
    bar_type[mfi_up & vol_up] = "green"
    bar_type[~mfi_up & ~vol_up] = "fade"
    bar_type[mfi_up & ~vol_up] = "fake"
    bar_type[~mfi_up & vol_up] = "squat"
    # First bar has no previous bar to compare against.
    bar_type[0] = "none"
    df["bar_type"] = bar_type

    df["ema20"] = ema(df["c"], EMA_PERIOD)
    return df
