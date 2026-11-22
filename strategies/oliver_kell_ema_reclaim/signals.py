"""Oliver Kell 20-EMA Reclaim signals.

LONG entry: the cross back above the 20 EMA after a pullback,
gated by the leader filter — close above a rising 200 SMA, 10
and 20 EMAs rising, pullback depth 5-19% off the trailing-20-bar
high, a close below the 20 EMA within the prior 10 bars, and
quiet volume (current volume below its 20-bar average).

SHORT entry is the mirror: close below a falling 200 SMA, 10/20
EMAs falling, 5-19% pullback off the trailing-20-bar low, a
close above the 20 EMA within the prior 10 bars, quiet volume,
and the cross back below the 20 EMA.

Exit: close back below the 20 EMA (long) / above it (short) —
the source's exit. The 3%-below-entry hard stop is approximated
by the 2xATR(14) harness stop (see risk.py / CALIBRATION.md).
All conditions read data through bar i; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.oliver_kell_ema_reclaim.indicators import DEPTH_HI, DEPTH_LO


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    depth = df["pullback_depth"].fillna(0.0)
    in_band = (depth >= DEPTH_LO) & (depth <= DEPTH_HI)

    long_setup = (
        (c > df["sma200"])
        & df["sma200_rising"].fillna(False)
        & df["ema10_rising"].fillna(False)
        & df["ema20_rising"].fillna(False)
        & in_band
        & df["touched_ema20"].fillna(False)
        & df["quiet_vol"].fillna(False)
    )
    short_setup = (
        (c < df["sma200"])
        & df["sma200_falling"].fillna(False)
        & df["ema10_falling"].fillna(False)
        & df["ema20_falling"].fillna(False)
        & in_band
        & df["touched_ema20_above"].fillna(False)
        & df["quiet_vol"].fillna(False)
    )
    long_entry = (B.crossed_above(c, df["ema20"]) & long_setup).fillna(False)
    short_entry = (B.crossed_below(c, df["ema20"]) & short_setup).fillna(False)
    long_exit = B.crossed_below(c, df["ema20"]).fillna(False)
    short_exit = B.crossed_above(c, df["ema20"]).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
