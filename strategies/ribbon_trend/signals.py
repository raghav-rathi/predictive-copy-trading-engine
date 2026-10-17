"""EMA ribbon signals.

long_entry  = ribbon flips to aligned-bull AND fan spread > 0.4%
              (avoids tangled-ribbon chop)
short_entry = ribbon flips to aligned-bear AND fan spread > 0.4%
long_exit   = ribbon loses bull alignment (e8 crosses under e55) OR
              fan compresses below 0.2% (exhaustion)
short_exit  = mirror
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies.ribbon_trend import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull, bear = df["ribbon_bull"], df["ribbon_bear"]
    fan = df["ribbon_fan"].fillna(0.0)
    flip_bull = bull & ~bull.shift(1).fillna(False) & (fan > I.MIN_FAN)
    flip_bear = bear & ~bear.shift(1).fillna(False) & (fan > I.MIN_FAN)
    lost_bull = ~bull
    lost_bear = ~bear
    exhausted = fan < I.MIN_FAN / 2
    df["long_entry"] = flip_bull.fillna(False)
    df["short_entry"] = flip_bear.fillna(False)
    df["long_exit"] = (lost_bull | exhausted).fillna(False)
    df["short_exit"] = (lost_bear | exhausted).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
