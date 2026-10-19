"""Bill Williams fractal breakout signals.

Long:  close crosses above the last CONFIRMED up-fractal level AND
       close > SMA200 (breakout of confirmed resistance in an uptrend).
Short: close crosses below the last CONFIRMED dn-fractal level AND
       close < SMA200 (breakdown of confirmed support in a downtrend).

Exits: a long exits on a cross back below the fractal level it broke
out above (cross_below close vs up_level) or on an opposing breakdown
(cross_below close vs dn_level -- the condition that would fire a
short entry); shorts mirror. The opposing-break clause also lets the
position flip when the other side's signal fires.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    up_lvl = df["up_level"]
    dn_lvl = df["dn_level"]
    uptrend = c > df["sma200"]
    downtrend = c < df["sma200"]
    df["long_entry"] = (B.crossed_above(c, up_lvl) & uptrend).fillna(False)
    df["short_entry"] = (B.crossed_below(c, dn_lvl) & downtrend).fillna(False)
    df["long_exit"] = (B.crossed_below(c, up_lvl) | B.crossed_below(c, dn_lvl)).fillna(False)
    df["short_exit"] = (B.crossed_above(c, dn_lvl) | B.crossed_above(c, up_lvl)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
