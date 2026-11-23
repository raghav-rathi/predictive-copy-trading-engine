"""Wilder ADX/DMI trend-system indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Wilder ADX(14) with +DI / -DI (base.adx): +DI and -DI are the
   Wilder-smoothed directional movements as a percentage of
   Wilder ATR; ADX is the smoothed absolute DI spread. This is
   Wilder's own construction from *New Concepts in Technical
   Trading Systems* (1978).
2. Trend gate: ADX > 25 — Wilder's own trend-strength rule. Below
   it the market is, by his definition, trendless and the system
   does not trade.
3. Cross: long_setup = +DI crosses above -DI while ADX > 25;
   short_setup = -DI crosses above +DI while ADX > 25
   (base.crossed_above, transition only — staying crossed does
   not re-trigger).
4. ATR(14) is carried for the risk layer.

Columns:
    adx, plus_di, minus_di, atr, long_setup, short_setup

Seeding / NaN handling: no indicator value is filled or
forward-filled — +DI/-DI are NaN for the first 13 bars and ADX
for longer (it smooths DX, which is itself NaN while the DI
spread is zero). The boolean setup columns are seeded
deterministically to False wherever any input is NaN
(.fillna(False)), so signal columns never leak NaN and no setup
can fire before ADX is valid. No lookahead: every input is
computed from bars <= i only.
"""

import pandas as pd

from strategies import base as B

ADX_N = 14
ADX_TREND = 25.0
ADX_EXIT = 20.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]

    dmi = B.adx(h, l, c, ADX_N)
    df["adx"] = dmi["adx"]
    df["plus_di"] = dmi["plus_di"]
    df["minus_di"] = dmi["minus_di"]

    df["atr"] = B.atr(h, l, c, 14)

    gate = (df["adx"] > ADX_TREND).fillna(False)
    df["long_setup"] = (B.crossed_above(df["plus_di"], df["minus_di"]) & gate).fillna(False).astype(bool)
    df["short_setup"] = (B.crossed_above(df["minus_di"], df["plus_di"]) & gate).fillna(False).astype(bool)
    return df
