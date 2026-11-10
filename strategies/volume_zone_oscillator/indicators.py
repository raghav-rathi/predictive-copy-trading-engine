"""Volume Zone Oscillator (VZO) indicators.

Faithful transcription of Walid Khalil & David Steckler's Volume Zone
Oscillator, "Fine-Tuning Trades with the Volume Zone Oscillator",
Technical Analysis of Stocks & Commodities, June 2011.

Published formula (all causal, bar i uses only data through bar i):
  R_t  = sign(close_t - close_{t-1}) * volume_t   (signed volume; 0 if
         the close is unchanged; 0 on the first bar, which has no
         previous close)
  VP_t = EMA(R, 14)
  TV_t = EMA(volume, 14)
  VZO_t = 100 * VP_t / TV_t   (bounded [-100, +100]; TV == 0 -> VZO = 0)

Trend context (Khalil's published system):
  EMA(60) of close + ADX(14) from strategies.base.
  Uptrend: close > EMA(60) and ADX > 18.
  Downtrend: close < EMA(60) and ADX > 18.

References:
  https://www.luxalgo.com/library/concept/volume-zone-oscillator/
  https://docs.wickra.org/Indicators/Indicator-Vzo
"""

import numpy as np
import pandas as pd

from strategies.base import adx, ema

VZO_PERIOD = 14
EMA_TREND_PERIOD = 60
ADX_PERIOD = 14
ADX_MIN = 18.0
VZO_OVERSOLD = -40.0
VZO_OVERBOUGHT = 40.0

INDICATOR_COLS = [
    "signed_volume",
    "vp",
    "tv",
    "vzo",
    "ema60",
    "adx",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].astype(float)
    v = df["v"].astype(float)

    # Signed volume: +volume on up closes, -volume on down closes, 0 on
    # unchanged closes (and on the first bar, which has no previous close).
    signed = np.sign(c.diff().fillna(0.0)) * v
    df["signed_volume"] = signed

    vp = ema(signed, VZO_PERIOD)
    tv = ema(v, VZO_PERIOD)
    df["vp"] = vp
    df["tv"] = tv
    # Guard TV == 0 (e.g. all-zero volume): VZO = 0. NaN TV during the
    # EMA warmup stays NaN, so no signal can fire before warmup.
    df["vzo"] = np.where(
        tv.fillna(0.0) == 0.0, 0.0, 100.0 * vp / tv.replace(0.0, np.nan)
    )
    df["vzo"] = pd.Series(df["vzo"], index=df.index).where(tv.notna())

    df["ema60"] = ema(c, EMA_TREND_PERIOD)
    df["adx"] = adx(df["h"], df["l"], c, ADX_PERIOD)["adx"]
    return df
