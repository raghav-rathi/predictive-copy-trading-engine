"""OBV trend signals: price/volume alignment entries, rollover exits.

Alignment state (long):  close > EMA(50) AND OBV > EMA(20,OBV) AND
3-bar OBV slope > 0. Short state mirrors it.
long_entry  = fresh alignment: aligned and NOT aligned on the prior bar
short_entry = fresh short alignment
long_exit   = close crosses below EMA(50) OR OBV crosses below its EMA(20)
short_exit  = close crosses above EMA(50) OR OBV crosses above its EMA(20)

The edge trigger prevents a persistent alignment from re-firing the
entry every bar; the harness only enters when flat anyway. Exits act on
the first sign of the volume trend rolling over, not just the price
filter. Execution is next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    above = df["c"] > df["ema50"]
    obv_up = (df["obv"] > df["obv_ema20"]) & (df["obv_slope"] > 0)
    below = df["c"] < df["ema50"]
    obv_dn = (df["obv"] < df["obv_ema20"]) & (df["obv_slope"] < 0)

    aligned_long = (above & obv_up).fillna(False)
    aligned_short = (below & obv_dn).fillna(False)

    df["long_entry"] = aligned_long & ~aligned_long.shift(1).fillna(False)
    df["short_entry"] = aligned_short & ~aligned_short.shift(1).fillna(False)
    df["long_exit"] = B.crossed_below(df["c"], df["ema50"]) | B.crossed_below(
        df["obv"], df["obv_ema20"]
    )
    df["short_exit"] = B.crossed_above(df["c"], df["ema50"]) | B.crossed_above(
        df["obv"], df["obv_ema20"]
    )
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
