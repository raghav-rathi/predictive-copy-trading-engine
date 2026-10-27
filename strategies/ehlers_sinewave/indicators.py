"""Ehlers Even Better Sinewave (causal approximation).

Pipeline (all causal, no lookahead):
  1. High-pass filter of median price with alpha1 from a 40-bar cycle
     (alpha1 = (1 - sin(360/40)) / cos(360/40)), Ehlers' roofing idea.
  2. 2-pole SuperSmoother (period 10) on the filtered series.
  3. Wave = mean of the last 3 filtered values; Pwr = mean of their
     squares; sine = wave / sqrt(pwr), clipped to [-1, 1]. In cycle
     mode this oscillates; in trend mode it rails near +-1, which is
     itself the mode signal (Ehlers).
  4. lead_sine = causal lead approximation: sine plus half its own
     3-bar slope, clipped. The classic rule is "sine crossing lead
     sine"; the lead here is extrapolated from past values only,
     never from future bars.

Columns: sine, lead_sine, atr.
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

DURATION = 40
SS_PERIOD = 10


def _supersmoother(p, period=SS_PERIOD):
    a1 = math.exp(-1.414 * math.pi / period)
    b1 = 2 * a1 * math.cos(math.radians(1.414 * 180 / period))
    c2, c3 = b1, -a1 * a1
    c1 = 1 - c2 - c3
    f = np.empty(len(p))
    if len(p) > 0:
        f[0] = p[0]
    if len(p) > 1:
        f[1] = p[1]
    for i in range(2, len(p)):
        f[i] = c1 * (p[i] + p[i - 1]) / 2 + c2 * f[i - 1] + c3 * f[i - 2]
    return f


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    price = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    n = len(price)
    alpha1 = (1 - math.sin(math.radians(360.0 / DURATION))) / math.cos(math.radians(360.0 / DURATION))
    hp = np.zeros(n)
    for i in range(2, n):
        hp[i] = (
            ((1 - alpha1 / 2) ** 2) * (price[i] - 2 * price[i - 1] + price[i - 2])
            + 2 * (1 - alpha1) * hp[i - 1]
            - ((1 - alpha1) ** 2) * hp[i - 2]
        )
    filt = _supersmoother(hp)
    fs = pd.Series(filt, index=df.index)
    wave = (fs + fs.shift(1) + fs.shift(2)) / 3
    pwr = (fs ** 2 + fs.shift(1) ** 2 + fs.shift(2) ** 2) / 3
    sine = (wave / np.sqrt(pwr.replace(0, np.nan))).clip(-1, 1)
    lead = (sine + 0.5 * (sine - sine.shift(3))).clip(-1, 1)
    df["sine"] = sine
    df["lead_sine"] = lead
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
