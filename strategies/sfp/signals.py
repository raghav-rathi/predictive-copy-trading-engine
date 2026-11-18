"""Swing Failure Pattern (SFP) signals.

Bullish SFP (long entry) on bar i: the low sweeps below the last
confirmed swing low (as of bar i-1) AND the close is back above
that same level AND volume spikes (> 1.5x SMA(volume, 20)).
Bearish SFP (short entry): the mirror — high above the last
confirmed swing high (as of bar i-1), close back below it, volume
spike.

Long exit: close back below the swept swing low (the level fails
again) OR a bearish SFP prints. Short exit: the mirror.

The swept level is always the level as of bar i-1 (shifted by 1):
a pivot confirming on bar i itself must not be swept and reclaimed
by the same bar. Signal columns are boolean, no NaN, no lookahead
(the harness executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sl_prev = df["swing_low"].shift(1)
    sh_prev = df["swing_high"].shift(1)
    vol_spike = (df["v"] > 1.5 * df["vol_ma20"]).fillna(False)
    bull_sfp = ((df["l"] < sl_prev) & (df["c"] > sl_prev)
                & vol_spike).fillna(False)
    bear_sfp = ((df["h"] > sh_prev) & (df["c"] < sh_prev)
                & vol_spike).fillna(False)
    df["long_entry"] = bull_sfp.astype(bool)
    df["short_entry"] = bear_sfp.astype(bool)
    df["long_exit"] = ((df["c"] < sl_prev) | bear_sfp).fillna(False).astype(bool)
    df["short_exit"] = ((df["c"] > sh_prev) | bull_sfp).fillna(False).astype(bool)
    return df
