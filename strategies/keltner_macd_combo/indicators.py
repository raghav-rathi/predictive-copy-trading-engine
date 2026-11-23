"""Keltner Channel + MACD combo indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Keltner Channel: mid = EMA(20) of close; bands = mid +/- 1.5 x
   ATR(10) (base.keltner). A close above the upper band is a
   volatility-expansion breakout in the Raschke sense.
2. MACD(12, 26, 9) (base.macd): line, signal, histogram. The
   histogram signs the momentum agreement — long only while the
   histogram is positive, short only while it is negative.
3. Breakout transition: long_break is true only on the bar where
   the close crosses from at/below the upper band to above it
   (prior close <= prior upper band); staying above the band does
   not re-trigger. Short_break is the mirror at the lower band.
4. Setup: long_setup = long_break AND macd_hist > 0;
   short_setup = short_break AND macd_hist < 0.
5. ATR(14) is carried for the risk layer.

Columns:
    kc_mid, kc_upper, kc_lower, macd, macd_signal, macd_hist,
    atr, long_break, short_break, long_setup, short_setup

Seeding / NaN handling: no indicator value is filled or
forward-filled — EMA(20) is NaN for the first 19 bars, ATR(10)
for the first 9, MACD for the first 25 and its signal/histogram
for the first ~33. The boolean setup/break columns are seeded
deterministically to False wherever any input is NaN
(.fillna(False)), so signal columns never leak NaN and no
setup can fire before every input is valid. No lookahead: every
input is computed from bars <= i only.
"""

import pandas as pd

from strategies import base as B

KC_EMA_N = 20
KC_ATR_N = 10
KC_MULT = 1.5
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    kc = B.keltner(h, l, c, ema_n=KC_EMA_N, atr_n=KC_ATR_N, k=KC_MULT)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]

    m = B.macd(c, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]

    df["atr"] = B.atr(h, l, c, 14)

    prev_c = c.shift(1)
    prev_upper = df["kc_upper"].shift(1)
    prev_lower = df["kc_lower"].shift(1)
    df["long_break"] = ((c > df["kc_upper"]) & (prev_c <= prev_upper)).fillna(False).astype(bool)
    df["short_break"] = ((c < df["kc_lower"]) & (prev_c >= prev_lower)).fillna(False).astype(bool)

    df["long_setup"] = (df["long_break"] & (df["macd_hist"] > 0)).fillna(False).astype(bool)
    df["short_setup"] = (df["short_break"] & (df["macd_hist"] < 0)).fillna(False).astype(bool)
    return df
