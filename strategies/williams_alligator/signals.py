"""Bill Williams' Alligator + fractal breakout signals ("Trading Chaos").

Long when a confirmed buy-fractal high breaks (close > fractal level) AND
the fractal level is above the teeth AND the Alligator is awake
(lips > teeth > jaw). Mirror for shorts (fractal below teeth,
lips < teeth < jaw).

Exits: the opposite fractal break, or the Alligator "falling asleep" —
long_exit when lips crosses below teeth, short_exit when lips crosses
above teeth. Risk-level exits (stop, max hold) come from risk.py.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    teeth = df["alligator_teeth"]
    lips = df["alligator_lips"]
    awake_long = df["gator_awake_long"].fillna(False)
    awake_short = df["gator_awake_short"].fillna(False)
    buy_break = (
        (c > df["fractal_buy_level"]) & (df["fractal_buy_level"] > teeth)
    ).fillna(False)
    sell_break = (
        (c < df["fractal_sell_level"]) & (df["fractal_sell_level"] < teeth)
    ).fillna(False)
    df["long_entry"] = (buy_break & awake_long).fillna(False).astype(bool)
    df["short_entry"] = (sell_break & awake_short).fillna(False).astype(bool)
    sleep_long = B.crossed_below(lips, teeth).fillna(False)
    sleep_short = B.crossed_above(lips, teeth).fillna(False)
    df["long_exit"] = (sleep_long | sell_break).fillna(False).astype(bool)
    df["short_exit"] = (sleep_short | buy_break).fillna(False).astype(bool)
    return df
