"""Donchian 20 breakout with an ADX(14) trend filter.

Donchian channel (same entry convention as strategies/donchian_channel):
the 20-bar highest high / lowest low. ADX(14) is Wilder's trend-strength
measure from strategies.base.adx (with +DI / -DI).

Columns:

    donchian_high_20 / donchian_low_20 / donchian_mid_20
    adx / plus_di / minus_di
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses bars through i only. Signals
compare the close to the PRIOR bar's channel values (shifted by 1 in
signals.py), so a close can never exceed its own bar's channel.
"""

import pandas as pd

from strategies import base as B

DONCHIAN_N = 20
ADX_N = 14
ADX_ENTRY = 25.0
ADX_EXIT = 20.0

INDICATOR_COLS = [
    "donchian_high_20",
    "donchian_low_20",
    "donchian_mid_20",
    "adx",
    "plus_di",
    "minus_di",
    "atr",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = B.donchian(df["h"], df["l"], DONCHIAN_N)
    df["donchian_high_20"] = d["donchian_high_20"]
    df["donchian_low_20"] = d["donchian_low_20"]
    df["donchian_mid_20"] = (df["donchian_high_20"] + df["donchian_low_20"]) / 2
    a = B.adx(df["h"], df["l"], df["c"], ADX_N)
    df["adx"] = a["adx"]
    df["plus_di"] = a["plus_di"]
    df["minus_di"] = a["minus_di"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
