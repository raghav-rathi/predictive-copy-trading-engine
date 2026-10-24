"""John Ehlers' Roofing Filter (Cycle Analytics).

Two stages, both causal (trailing windows only, no lookahead):

1. High-pass filter tuned to a 48-bar cycle. With alpha = 2*pi/48:

       y[i] = (1 - alpha/2)^2 * (x[i] - 2*x[i-1] + x[i-2])
              + 2*(1 - alpha) * y[i-1] - (1 - alpha)^2 * y[i-2]

   The high-pass removes the trend (DC and slow drift) so the output
   oscillates around zero; the recursion's poles sit on the 48-bar
   cycle, so a 48-bar cyclic component passes with limited
   attenuation while slower components are rejected. The first two
   outputs are seeded to 0 (no history exists before bar 0).

2. SuperSmoother (10-bar, Ehlers 2-pole coefficients) applied to the
   high-pass output, to remove the high-frequency noise the
   differentiator-style high-pass amplifies:

       a1 = exp(-1.414 * pi / period)
       b1 = 2 * a1 * cos(1.414 * 180 / period)      (argument in degrees)
       c2 = b1
       c3 = -a1 * a1
       c1 = 1 - c2 - c3
       f[i] = c1 * (y[i] + y[i-1]) / 2 + c2 * f[i-1] + c3 * f[i-2]

   Also seeded 0 for the first two bars. Unity gain at DC
   (c1 / (1 - c2 - c3) == 1), so the smoother does not rescale the
   roofing line.

Columns:

    roofing_hp -- high-pass output (pre-smoothing, for inspection)
    roofing    -- the roofing line itself (SuperSmoother of roofing_hp)
    atr        -- Wilder ATR(14) for the risk layer

The trend signal IS the roofing line: it is a detrended, smoothed
cycle estimate, so its zero crossings mark cycle turns.
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

CYCLE = 48        # shipped default: high-pass tuned cycle length
SS_PERIOD = 10    # shipped default: SuperSmoother period


def roofing_coefs(cycle: int = CYCLE) -> dict:
    """High-pass recursion coefficients for a tuned ``cycle``."""
    alpha = 2 * math.pi / cycle
    return {
        "alpha": alpha,
        "a": (1 - alpha / 2) ** 2,
        "b": 2 * (1 - alpha),
        "c": (1 - alpha) ** 2,
    }


def supersmoother_coefs(period: int = SS_PERIOD) -> dict:
    """Ehlers SuperSmoother coefficients for a cutoff ``period``."""
    a1 = math.exp(-1.414 * math.pi / period)
    b1 = 2 * a1 * math.cos(math.radians(1.414 * 180 / period))
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    return {"a1": a1, "b1": b1, "c1": c1, "c2": c2, "c3": c3}


def roofing_filter(price: pd.Series, cycle: int = CYCLE,
                   ss_period: int = SS_PERIOD) -> pd.Series:
    """Roofing line: high-pass(cycle) followed by SuperSmoother(period)."""
    x = price.to_numpy(dtype=float)
    n = len(x)
    k = roofing_coefs(cycle)
    a, b, c = k["a"], k["b"], k["c"]
    hp = np.zeros(n)
    for i in range(2, n):
        hp[i] = (a * (x[i] - 2 * x[i - 1] + x[i - 2])
                 + b * hp[i - 1] - c * hp[i - 2])
    s = supersmoother_coefs(ss_period)
    c1, c2, c3 = s["c1"], s["c2"], s["c3"]
    f = np.zeros(n)
    for i in range(2, n):
        f[i] = c1 * (hp[i] + hp[i - 1]) / 2 + c2 * f[i - 1] + c3 * f[i - 2]
    return pd.Series(f, index=price.index)


def high_pass(price: pd.Series, cycle: int = CYCLE) -> pd.Series:
    """High-pass stage only (exposed for unit tests)."""
    x = price.to_numpy(dtype=float)
    n = len(x)
    k = roofing_coefs(cycle)
    a, b, c = k["a"], k["b"], k["c"]
    hp = np.zeros(n)
    for i in range(2, n):
        hp[i] = (a * (x[i] - 2 * x[i - 1] + x[i - 2])
                 + b * hp[i - 1] - c * hp[i - 2])
    return pd.Series(hp, index=price.index)


def add_indicators(df: pd.DataFrame, cycle: int = CYCLE,
                   ss_period: int = SS_PERIOD) -> pd.DataFrame:
    df = df.copy()
    df["roofing_hp"] = high_pass(df["c"], cycle)
    df["roofing"] = roofing_filter(df["c"], cycle, ss_period)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
