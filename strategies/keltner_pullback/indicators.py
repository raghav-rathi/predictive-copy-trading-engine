"""Keltner pullback indicators (Chester Keltner channel, causal).

Trend + pullback, not breakout: that is what separates this from
keltner_rsi (breakout above the band with an RSI filter),
keltner_adx (breakout with an ADX filter) and keltner_squeeze
(band-width contraction). Here the trend is set by the 50-bar
EMA -- price above a rising EMA50 is an uptrend -- and the
Keltner midline (EMA20) is the pullback target: price dips to
or through the midline and then closes back above it, rejoining
the trend at a discount. Bearish mirrors.

Columns:
    kc_mid, kc_upper, kc_lower -- Keltner channel (EMA20 mid,
        ATR(10) x 1.5 bands) via strategies.base.keltner
    ema50      -- EMA(50) trend filter
    ema50_up   -- EMA50 rising vs prior bar
    ema50_dn   -- EMA50 falling vs prior bar
    atr        -- Wilder ATR(14) for the risk layer
"""

import pandas as pd

from strategies import base as B

EMA_MID = 20
ATR_N = 10
KC_K = 1.5
EMA_TREND = 50


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"], ema_n=EMA_MID, atr_n=ATR_N, k=KC_K)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["ema50"] = B.ema(df["c"], EMA_TREND)
    df["ema50_up"] = (df["ema50"] > df["ema50"].shift(1)).fillna(False)
    df["ema50_dn"] = (df["ema50"] < df["ema50"].shift(1)).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
