"""Donchian + MACD signals.

Long entry:  close breaks above the trailing 20-bar high AND MACD
             histogram > 0.
Short entry: close breaks below the trailing 20-bar low AND MACD
             histogram < 0.
Long exit:   close below the trailing 20-bar low OR MACD histogram
             flips negative.
Short exit:  close above the trailing 20-bar high OR MACD histogram
             flips positive.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    breakout_up = (df["c"] > df["donchian_high_20"]).fillna(False)
    breakout_dn = (df["c"] < df["donchian_low_20"]).fillna(False)
    hist_pos = (df["macd_hist"] > 0).fillna(False)
    hist_neg = (df["macd_hist"] < 0).fillna(False)
    df["long_entry"] = (breakout_up & hist_pos).astype(bool)
    df["short_entry"] = (breakout_dn & hist_neg).astype(bool)
    df["long_exit"] = (breakout_dn | hist_neg).astype(bool)
    df["short_exit"] = (breakout_up | hist_pos).astype(bool)
    return df
