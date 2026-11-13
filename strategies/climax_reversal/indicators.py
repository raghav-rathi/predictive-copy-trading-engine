"""Wyckoff climax reversal indicators.

Wyckoff's law of effort vs result: volume is the effort, the price
move is the result. A climax bar is heavy effort with no result —
the trend exhausts itself at the extreme:

Buying climax (short signal):
    new 20-bar high AND volume > 2x the trailing 20-bar mean volume
    AND close in the LOWER third of the bar's range
    (buyers pushed to a new high on huge volume but the close fell
    back — supply absorbed the buying).

Selling climax (long signal):
    new 20-bar low AND volume > 2x the trailing 20-bar mean volume
    AND close in the UPPER third of the bar's range
    (sellers pushed to a new low on huge volume but the close
    recovered — demand absorbed the selling).

The volume mean uses the PREVIOUS 20 bars (shifted by 1), so the
current bar's own spike does not dilute the comparison. The
20-bar high/low includes the current bar (a new extreme is only
known at the close).

Columns:

    high_20, low_20    -- trailing 20-bar high/low (incl. current)
    vol_mean_20         -- mean volume of the previous 20 bars
    vol_ratio           -- volume / vol_mean_20
    close_pos           -- (close - low) / (high - low), NaN on zero range
    buying_climax       -- bool, as defined above
    selling_climax      -- bool, as defined above
    atr                 -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CLIMAX_N = 20
VOL_MULT = 2.0

INDICATOR_COLS = ["high_20", "low_20", "vol_mean_20", "vol_ratio",
                  "close_pos", "buying_climax", "selling_climax", "atr"]


def add_indicators(df: pd.DataFrame, n: int = CLIMAX_N,
                   vol_mult: float = VOL_MULT) -> pd.DataFrame:
    df = df.copy()
    high20 = df["h"].rolling(n, min_periods=n).max()
    low20 = df["l"].rolling(n, min_periods=n).min()
    vol_mean = df["v"].rolling(n, min_periods=n).mean().shift(1)
    vol_ratio = df["v"] / vol_mean
    bar_range = (df["h"] - df["l"]).replace(0, np.nan)
    close_pos = (df["c"] - df["l"]) / bar_range
    is_new_high = (df["h"] >= high20).fillna(False)
    is_new_low = (df["l"] <= low20).fillna(False)
    vol_spike = (vol_ratio > vol_mult).fillna(False)
    buying = is_new_high & vol_spike & (close_pos <= 1.0 / 3.0).fillna(False)
    selling = is_new_low & vol_spike & (close_pos >= 2.0 / 3.0).fillna(False)
    df["high_20"] = high20
    df["low_20"] = low20
    df["vol_mean_20"] = vol_mean
    df["vol_ratio"] = vol_ratio
    df["close_pos"] = close_pos
    df["buying_climax"] = buying.astype(bool)
    df["selling_climax"] = selling.astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
