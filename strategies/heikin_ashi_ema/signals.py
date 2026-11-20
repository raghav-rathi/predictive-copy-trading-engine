"""Heikin Ashi + EMA signals.

Long entry:  bullish Heikin Ashi candle (HA close > HA open) AND
             EMA(9) > EMA(21) AND close > EMA(50).
Short entry: bearish Heikin Ashi candle (HA close < HA open) AND
             EMA(9) < EMA(21) AND close < EMA(50).
Long exit:   HA candle flips bearish OR EMA(9) crosses below EMA(21).
Short exit:  HA candle flips bullish OR EMA(9) crosses above EMA(21).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ha_bull = (df["ha_close"] > df["ha_open"]).fillna(False)
    ha_bear = (df["ha_close"] < df["ha_open"]).fillna(False)
    ema_up = (df["ema_fast"] > df["ema_mid"]).fillna(False)
    ema_dn = (df["ema_fast"] < df["ema_mid"]).fillna(False)
    above_slow = (df["c"] > df["ema_slow"]).fillna(False)
    below_slow = (df["c"] < df["ema_slow"]).fillna(False)
    df["long_entry"] = (ha_bull & ema_up & above_slow).astype(bool)
    df["short_entry"] = (ha_bear & ema_dn & below_slow).astype(bool)
    df["long_exit"] = (ha_bear | ema_dn).astype(bool)
    df["short_exit"] = (ha_bull | ema_up).astype(bool)
    return df
