"""Gaussian filter trend -- John Ehlers, "Rocket Science for Traders" Ch. 15.

4-pole recursive Gaussian filter. Per-stage coefficient from the
critical period (the period attenuated by 50%, -3 dB):

    alpha = (1 - sin(2*pi/period)) / cos(2*pi/period)

4-pole recursion (g = input series, f = filter output):

    f = alpha^4 * g
      + 4*(1-alpha)   * f[1]
      - 6*(1-alpha)^2 * f[2]
      + 4*(1-alpha)^3 * f[3]
      -   (1-alpha)^4 * f[4]

The coefficients are the binomial expansion of a 4-stage cascade of
identical single-pole smoothers, so the combined response approaches
the Gaussian bell: better high-frequency rejection than an EMA with
about half the lag of a Butterworth of the same order. Lag of an
N-pole filter is ~N*P/pi^2 bars (fast 10 -> ~4 bars, slow 30 -> ~12).

Two filters on close: period 10 and period 30. The crossover is the
trend signal -- but see the CORRECTION below: with Ehlers' alpha
formula the LONGER-period filter is the FASTER tracker, so the
crossover is "period-30 line crosses above the period-10 line" for
longs, not the other way round.

CORRECTION (verified, see CALIBRATION.md): alpha = (1-sin(2*pi/P)) /
cos(2*pi/P) INCREASES with P (0.5095 at P=10, 0.8098 at P=30), so
the per-stage pole b = 1-alpha is SMALLER for the longer period and
the group delay 4*b/(1-b) is 3.85 bars for P=10 but only 0.94 bars
for P=30. Measured on a rising ramp (slope 0.1/bar) the P=30 line
sits 0.094 below price while the P=10 line sits 0.385 below it, and
on a sine wave the P=10 line crosses above the P=30 line at price
TOPS and below it at price BOTTOMS. The formula and the 4-pole
recursion are Ehlers' published forms (verified against the Loxx
expansion and the (1-sin)/cos form used in this repo's
ehlers_sinewave); what is corrected is the fast/slow ROLE assignment:
the P=30 filter is the fast tracker, the P=10 filter the slow
baseline. Shipping the brief's literal "P=10 crosses above P=30 =
long" would buy tops and sell bottoms. The columns are therefore
named by period (gf_p10, gf_p30) with no fast/slow labels, and the
signals trade the measured crossover direction.

Filter stages are seeded to the first four closes (Ehlers' "special
initialization" so the filter works from the first bars); the
coefficient bracket sums to exactly 1, so a constant input passes
through unchanged.

Columns:

    gf_p10  -- 4-pole Gaussian filter of close, period 10 (slow baseline)
    gf_p30  -- 4-pole Gaussian filter of close, period 30 (fast tracker)
    atr     -- Wilder ATR(14) for the risk layer

No lookahead: the recursion on bar j uses closes and filter outputs
through bar j only.
"""

import math

import numpy as np
import pandas as pd

FAST_PERIOD = 10  # shipped default (measured SLOW baseline -- see docstring)
SLOW_PERIOD = 30  # shipped default (measured FAST tracker -- see docstring)
POLES = 4         # shipped default (Ehlers' cap)


def alpha(period: float) -> float:
    """Per-stage coefficient for a Gaussian filter of critical period."""
    w = 2.0 * math.pi / period
    return (1.0 - math.sin(w)) / math.cos(w)


def gaussian_filter(s: pd.Series, period: float, poles: int = POLES) -> pd.Series:
    """N-pole recursive Gaussian filter (N <= 4)."""
    if poles not in (1, 2, 3, 4):
        raise ValueError(f"poles must be 1-4, got {poles}")
    a = alpha(period)
    b = 1.0 - a
    g = s.to_numpy(dtype=float)
    n = len(g)
    f = np.full(n, np.nan)
    if n == 0:
        return pd.Series(f, index=s.index)
    # Seed the first `poles` outputs to the input (Ehlers initialization);
    # the coefficient bracket sums to 1, so a constant input is preserved.
    seed = min(poles, n)
    f[:seed] = g[:seed]
    if poles == 1:
        for i in range(1, n):
            f[i] = a * g[i] + b * f[i - 1]
    elif poles == 2:
        for i in range(2, n):
            f[i] = a**2 * g[i] + 2 * b * f[i - 1] - b**2 * f[i - 2]
    elif poles == 3:
        for i in range(3, n):
            f[i] = (a**3 * g[i] + 3 * b * f[i - 1]
                    - 3 * b**2 * f[i - 2] + b**3 * f[i - 3])
    else:
        a4 = a**4
        for i in range(4, n):
            f[i] = (a4 * g[i] + 4 * b * f[i - 1] - 6 * b**2 * f[i - 2]
                    + 4 * b**3 * f[i - 3] - b**4 * f[i - 4])
    return pd.Series(f, index=s.index)


def add_indicators(df: pd.DataFrame, fast: float = FAST_PERIOD,
                   slow: float = SLOW_PERIOD,
                   poles: int = POLES) -> pd.DataFrame:
    from strategies import base as B

    df = df.copy()
    df["gf_p10"] = gaussian_filter(df["c"], fast, poles)
    df["gf_p30"] = gaussian_filter(df["c"], slow, poles)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
