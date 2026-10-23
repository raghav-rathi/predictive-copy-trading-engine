"""Elder Ray signals (Elder's exhaustion-with-trend entries).

long_entry  = EMA(13) rising AND Bear Power < 0 turning up
              (sellers exhausted, bulls still in control)
short_entry = EMA(13) falling AND Bull Power > 0 turning down
              (buyers exhausted, bears still in control)
long_exit   = Bull Power crosses below 0 (buyers lost the highs)
short_exit  = Bear Power crosses above 0 (sellers lost the lows)
Execution next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ema = df["elder_ema"]
    bull, bear = df["bull_power"], df["bear_power"]
    ema_up = (ema > ema.shift(1)).fillna(False)
    ema_dn = (ema < ema.shift(1)).fillna(False)
    bear_turning_up = (bear > bear.shift(1)) & ~(bear.shift(1) > bear.shift(2))
    bull_turning_dn = (bull < bull.shift(1)) & ~(bull.shift(1) < bull.shift(2))
    df["long_entry"] = (bear_turning_up & (bear < 0) & ema_up).fillna(False)
    df["short_entry"] = (bull_turning_dn & (bull > 0) & ema_dn).fillna(False)
    df["long_exit"] = ((bull < 0) & (bull.shift(1) >= 0)).fillna(False)
    df["short_exit"] = ((bear > 0) & (bear.shift(1) <= 0)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
