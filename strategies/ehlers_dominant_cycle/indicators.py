"""Ehlers dominant-cycle measurement indicators.

John F. Ehlers, "Cycle Analytics for Traders" (2013), band-pass
filter / dominant-cycle chapter. The close is first passed
through Ehlers' one-pole high-pass detrender, then through the
two-pole band-pass resonator:

    beta  = cos(2*pi / period)
    gamma = 1 / cos(4*pi * bandwidth / period)
    alpha = gamma - sqrt(gamma^2 - 1)
    BP_t  = 0.5*(1-alpha)*(x_t - x_{t-2})
            + beta*(1+alpha)*BP_{t-1} - alpha*BP_{t-2}

with period = 20 and bandwidth = 0.7 (an octave-wide pass
band per the book). The high-pass cutoff sits one octave
below the half-bandwidth edge of the pass band: the lower
pass-band edge is at period 20 / (1 - 0.7/2) = 30.8 bars, so
the detrender cutoff is 2 * 30.8 = 61.5 bars. The high-pass
is Ehlers' one-pole form:

    a_hp = (1 - sin(2*pi / P_hp)) / cos(2*pi / P_hp)
    HP_t = 0.5*(1+a_hp)*(x_t - x_{t-1}) + a_hp*HP_{t-1}

The dominant cycle period is measured from the band-pass
output: the period is twice the bars between successive BP
zero crossings, assigned at the crossing bar that completes
the half-cycle, forward-filled, smoothed with a 10-bar SMA
and clamped to [6, 50]. Before the first crossing the
diagnostic defaults to the centre period (20).

Columns:
    hp          -- high-pass detrended close
    bp          -- band-pass resonator output (on hp)
    dom_cycle   -- dominant cycle period, bars (diagnostic)
    atr14       -- ATR(14), diagnostic (the harness computes its own)

No lookahead: both filters are causal recursions and the
cycle measurement uses only crossings at or before the
current bar.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 20
BANDWIDTH = 0.7
# Lower pass-band edge period = PERIOD / (1 - BANDWIDTH/2); the
# high-pass cutoff is one octave below it (period doubled).
HP_PERIOD = 2.0 * PERIOD / (1.0 - BANDWIDTH / 2.0)
CYCLE_SMA = 10
CYCLE_MIN = 6.0
CYCLE_MAX = 50.0


def _resonator_coeffs(period: float, bandwidth: float):
    beta = np.cos(2.0 * np.pi / period)
    gamma = 1.0 / np.cos(4.0 * np.pi * bandwidth / period)
    alpha = gamma - np.sqrt(gamma * gamma - 1.0)
    return beta, alpha


def _high_pass(x: np.ndarray, cutoff_period: float) -> np.ndarray:
    a = (1.0 - np.sin(2.0 * np.pi / cutoff_period)) / np.cos(2.0 * np.pi / cutoff_period)
    out = np.zeros(len(x))
    for i in range(1, len(x)):
        out[i] = 0.5 * (1.0 + a) * (x[i] - x[i - 1]) + a * out[i - 1]
    return out


def _band_pass(x: np.ndarray, period: float, bandwidth: float) -> np.ndarray:
    beta, alpha = _resonator_coeffs(period, bandwidth)
    out = np.zeros(len(x))
    for i in range(2, len(x)):
        out[i] = (
            0.5 * (1.0 - alpha) * (x[i] - x[i - 2])
            + beta * (1.0 + alpha) * out[i - 1]
            - alpha * out[i - 2]
        )
    return out


def _dominant_cycle(bp: np.ndarray, period: float, sma_n: int) -> np.ndarray:
    """2x bars between successive BP zero crossings, SMA-smoothed."""
    n = len(bp)
    sign = np.where(bp > 0, 1, np.where(bp < 0, -1, 0))
    # forward-fill zero signs (exact-zero BP readings keep the
    # previous sign; leading zeros stay 0 and cannot cross).
    for i in range(1, n):
        if sign[i] == 0:
            sign[i] = sign[i - 1]
    cross_idx = np.where((sign[1:] != sign[:-1]) & (sign[1:] != 0) & (sign[:-1] != 0))[0] + 1
    raw = np.full(n, np.nan)
    for k in range(1, len(cross_idx)):
        raw[cross_idx[k]] = 2.0 * (cross_idx[k] - cross_idx[k - 1])
    s = pd.Series(raw).ffill().fillna(period)
    out = s.rolling(sma_n, min_periods=1).mean().to_numpy()
    return np.clip(out, CYCLE_MIN, CYCLE_MAX)


def add_indicators(
    df: pd.DataFrame,
    period: int = PERIOD,
    bandwidth: float = BANDWIDTH,
    cycle_sma: int = CYCLE_SMA,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    hp = _high_pass(c, HP_PERIOD)
    bp = _band_pass(hp, period, bandwidth)
    df["hp"] = hp
    df["bp"] = bp
    df["dom_cycle"] = _dominant_cycle(bp, period, cycle_sma)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
