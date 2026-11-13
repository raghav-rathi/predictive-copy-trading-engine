"""Volume Spread Analysis indicators (Tom Williams, Master the Markets).

VSA reads the relationship between a bar's spread (high - low),
its volume, and its close — Wyckoff's law of effort vs result:
volume is the effort, the spread and close are the result. A narrow
spread on low volume after a move means the side that should be
pushing is absent; a wide spread on climactic volume into a close
that fails to hold the extreme means absorption.

Bar taxonomy (all causal, volume compared to trailing bars only):

    spread      = h - l
    narrow      = spread < 0.5 * ATR(20)
    down bar    = close < prior close; up bar = close > prior close
    vol_low2    = volume lower than EACH of the previous two bars
    vol_mean20  = trailing 20-bar mean volume

    NO-SUPPLY   = down bar + narrow + vol_low2
                  (sellers absent on a down bar -> long)
    NO-DEMAND   = up bar + narrow + vol_low2
                  (buyers absent on an up bar -> short)
    STOPPING VOLUME = down bar after a 10-bar decline
                  (close below close 10 bars ago) + volume > 2x
                  vol_mean20 + close in the UPPER half of its
                  range (professional buying absorbs the selling)
                  -> long
    UPTHRUST    = bar pushes above the prior 20-bar high then
                  closes in the LOWER third of its range on volume
                  > 1.5x vol_mean20 (a failed probe above supply)
                  -> short

Columns:

    vsa_spread, vsa_atr20, vsa_narrow, vsa_vol_mean20,
    vsa_no_supply, vsa_no_demand, vsa_stopping_volume,
    vsa_upthrust, atr (Wilder ATR(14) for the risk layer)

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

ATR_SPREAD = 20
VOL_MEAN = 20
DECLINE_N = 10
STOPPING_VOL_MULT = 2.0
UPTHRUST_VOL_MULT = 1.5
UPTHRUST_HIGH_N = 20

INDICATOR_COLS = ["vsa_spread", "vsa_atr20", "vsa_narrow",
                  "vsa_vol_mean20", "vsa_no_supply", "vsa_no_demand",
                  "vsa_stopping_volume", "vsa_upthrust", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    spread = df["h"] - df["l"]
    atr20 = B.atr(df["h"], df["l"], df["c"], ATR_SPREAD)
    narrow = spread < 0.5 * atr20
    prev_c = df["c"].shift(1)
    down_bar = df["c"] < prev_c
    up_bar = df["c"] > prev_c
    vol_low2 = (df["v"] < df["v"].shift(1)) & (df["v"] < df["v"].shift(2))
    vol_mean20 = df["v"].rolling(VOL_MEAN, min_periods=VOL_MEAN).mean()
    decline = df["c"] < df["c"].shift(DECLINE_N)
    upper_half = df["c"] > (df["h"] + df["l"]) / 2
    lower_third = df["c"] < df["l"] + spread / 3
    prior20_high = df["h"].shift(1).rolling(UPTHRUST_HIGH_N,
                                            min_periods=UPTHRUST_HIGH_N).max()

    no_supply = down_bar & narrow & vol_low2
    no_demand = up_bar & narrow & vol_low2
    stopping_volume = (down_bar & decline
                       & (df["v"] > STOPPING_VOL_MULT * vol_mean20)
                       & upper_half)
    upthrust = ((df["h"] > prior20_high) & lower_third
                & (df["v"] > UPTHRUST_VOL_MULT * vol_mean20))

    df["vsa_spread"] = spread
    df["vsa_atr20"] = atr20
    df["vsa_narrow"] = narrow.fillna(False).astype(bool)
    df["vsa_vol_mean20"] = vol_mean20
    df["vsa_no_supply"] = no_supply.fillna(False).astype(bool)
    df["vsa_no_demand"] = no_demand.fillna(False).astype(bool)
    df["vsa_stopping_volume"] = stopping_volume.fillna(False).astype(bool)
    df["vsa_upthrust"] = upthrust.fillna(False).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
