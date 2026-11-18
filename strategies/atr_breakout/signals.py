"""ATR expansion breakout signals.

Long entry:  close > range_high + 0.25*ATR AND ATR > ATR_MA20 AND
             range_ok (tight range).
Short entry: close < range_low - 0.25*ATR AND ATR > ATR_MA20 AND
             range_ok.
Long exit:   close < range_high (back inside the range) OR
             ATR < ATR_MA20 (expansion regime gone).
Short exit:  close > range_low OR ATR < ATR_MA20.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). The breakout levels are the
previous-20-bar close extremes, so a close can break them; the
0.25*ATR buffer is added to the level on the current bar, which
uses only the current bar's own ATR (known at its close).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    atr = df["atr"]
    atr_ma = df["atr_ma20"]
    expanding = (atr > atr_ma).fillna(False)
    faded = (atr < atr_ma).fillna(False)
    range_ok = df["range_ok"].fillna(False)
    long_break = (df["c"] > df["range_high_20"] + 0.25 * atr).fillna(False)
    short_break = (df["c"] < df["range_low_20"] - 0.25 * atr).fillna(False)
    df["long_entry"] = (long_break & expanding & range_ok).astype(bool)
    df["short_entry"] = (short_break & expanding & range_ok).astype(bool)
    df["long_exit"] = ((df["c"] < df["range_high_20"]).fillna(False) | faded).astype(bool)
    df["short_exit"] = ((df["c"] > df["range_low_20"]).fillna(False) | faded).astype(bool)
    return df
