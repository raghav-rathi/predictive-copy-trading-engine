"""Ehlers universal oscillator (adaptive band-pass) indicators.

John F. Ehlers, "Cycle Analytics for Traders" (2013), band-pass
filter chapter — the same two-pole resonator as the dominant
cycle meter, but as a trading oscillator: median price
((h+l)/2) through a tighter resonator (period 20, bandwidth
0.3), AGC-normalized by its rolling 100-bar RMS, with a
trigger line of the normalized output delayed one bar and
scaled 0.9 (Ehlers' adaptive band-pass trigger convention).

    beta  = cos(2*pi / period)
    gamma = 1 / cos(4*pi * bandwidth / period)
    alpha = gamma - sqrt(gamma^2 - 1)
    BP_t  = 0.5*(1-alpha)*(med_t - med_{t-2})
            + beta*(1+alpha)*BP_{t-1} - alpha*BP_{t-2}
    bp_norm_t = BP_t / RMS_100(BP)   (0 when the RMS is 0)
    trigger_t = 0.9 * bp_norm_{t-1}

The RMS window uses min_periods=1 (an expanding window until
100 bars have accumulated) so the normalized output is defined
from the first bar; after 100 bars it is exactly the rolling
100-bar RMS. This is causal throughout.

Columns:
    bp        -- band-pass resonator output on median price
    bp_norm   -- AGC-normalized band-pass output
    trigger   -- 0.9 * bp_norm delayed 1 bar
    atr14     -- ATR(14), diagnostic (the harness computes its own)

No lookahead: the resonator is a causal recursion, the RMS
uses only past bars, and the trigger is the prior bar's
normalized value.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 20
BANDWIDTH = 0.3
RMS_WINDOW = 100
TRIGGER_SCALE = 0.9


def _resonator_coeffs(period: float, bandwidth: float):
    beta = np.cos(2.0 * np.pi / period)
    gamma = 1.0 / np.cos(4.0 * np.pi * bandwidth / period)
    alpha = gamma - np.sqrt(gamma * gamma - 1.0)
    return beta, alpha


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


def add_indicators(
    df: pd.DataFrame,
    period: int = PERIOD,
    bandwidth: float = BANDWIDTH,
    rms_window: int = RMS_WINDOW,
    trigger_scale: float = TRIGGER_SCALE,
) -> pd.DataFrame:
    df = df.copy()
    med = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    bp = _band_pass(med, period, bandwidth)
    bp_s = pd.Series(bp, index=df.index)
    rms = np.sqrt((bp_s ** 2).rolling(rms_window, min_periods=1).mean())
    rms_v = rms.to_numpy()
    bp_norm = np.zeros_like(bp)
    np.divide(bp, rms_v, out=bp_norm, where=rms_v > 0)
    df["bp"] = bp
    df["bp_norm"] = bp_norm
    df["trigger"] = pd.Series(bp_norm, index=df.index).shift(1) * trigger_scale
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
