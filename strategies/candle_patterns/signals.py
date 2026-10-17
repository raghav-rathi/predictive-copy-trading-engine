"""Candlestick pattern signals.

long_entry  = bullish engulfing OR bullish pin bar
short_entry = bearish engulfing OR bearish pin bar
long_exit   = opposite pattern (bearish engulfing / bearish pin)
short_exit  = opposite pattern (bullish engulfing / bullish pin)
The pin-bar extreme doubles as the natural invalidation; the harness
hard stop is set at 1.5xATR approximating the pattern extreme.
Execution next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["bull_engulf"] | df["bull_pin"]
    bear = df["bear_engulf"] | df["bear_pin"]
    df["long_entry"] = bull.fillna(False)
    df["short_entry"] = bear.fillna(False)
    df["long_exit"] = bear.fillna(False)
    df["short_exit"] = bull.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
