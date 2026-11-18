"""Change of Character (ChoCh) signals.

Bearish ChoCh (short entry) on bar i: the trend was an uptrend as
of bar i-1 AND the close breaks below the protected higher low (as
of bar i-1) AND the breaking candle's body is displacement-sized
(|close - open| > 1.5x ATR(14)). Bullish ChoCh (long entry): the
mirror in a downtrend against the protected lower high.

Long exit: a bearish ChoCh prints OR the close exceeds the last
swing high (the break failed / head exceeded). Short exit: the
mirror. Trend and protected levels are always read as of bar i-1
(shifted by 1): a ChoCh must break structure that was established
before the breaking bar, never structure confirmed by that bar
itself. Signal columns are boolean, no NaN, no lookahead (the
harness executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    trend_prev = df["trend"].shift(1).fillna(0)
    pl_prev = df["protected_low"].shift(1)
    ph_prev = df["protected_high"].shift(1)
    sh_prev = df["swing_high"].shift(1)
    sl_prev = df["swing_low"].shift(1)
    displacement = (df["body_atr"] > 1.5).fillna(False)
    bear_choch = ((trend_prev == 1) & (df["c"] < pl_prev)
                  & displacement).fillna(False)
    bull_choch = ((trend_prev == -1) & (df["c"] > ph_prev)
                  & displacement).fillna(False)
    df["long_entry"] = bull_choch.astype(bool)
    df["short_entry"] = bear_choch.astype(bool)
    df["long_exit"] = (bear_choch | (df["c"] > sh_prev).fillna(False)).astype(bool)
    df["short_exit"] = (bull_choch | (df["c"] < sl_prev).fillna(False)).astype(bool)
    return df
