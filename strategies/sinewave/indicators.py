"""Ehlers SineWave indicators (John F. Ehlers, Cybernetic Analysis for
Stocks and Futures, 2004; TA-Lib HT_SINE).

Pipeline (all causal, no lookahead):

  1. Median price p = (h + l) / 2.
  2. Detrend with Ehlers' high-pass (roofing) filter for a 40-bar
     cycle: alpha1 = (1 - sin(2*pi/40)) / cos(2*pi/40),
     hp[i] = ((1 - alpha1/2)^2) * (p[i] - 2*p[i-1] + p[i-2])
             + 2*(1 - alpha1)*hp[i-1] - (1 - alpha1)^2*hp[i-2],
     with hp[0] = hp[1] = 0.
  3. Hilbert transform of the detrended series via a causal FIR
     Hilbert transformer: 51 taps, ideal impulse response
     h[n] = 2 / (pi*n) for odd n, 0 for even n, Hamming-windowed,
     centred at tap 25 (group delay 25 bars).
         Q[i] = sum_k h[k] * d[i-k]          (quadrature)
         I[i] = d[i-25]                      (in-phase, delay-aligned)
     Both use data through bar i's close only.
  4. Instantaneous phase = atan2(Q, I); the phase is NaN until the
     full 51-tap window is available (bar 50).
  5. sine = sin(phase), lead_sine = sin(phase + pi/4).

Sign convention: the ideal Hilbert transform sends cos -> sin and
sin -> -cos, so for a detrended cycle d = A*sin(theta) the measured
phase is theta - 90 degrees. The constant -90 degree offset does not
affect the sine/lead-sine crosses, which are the trade signal.

Columns: sine, lead_sine, phase, atr.

Distinct from strategies/ehlers_sinewave (the "Even Better Sinewave"
approximation: sine = wave / sqrt(pwr) with a slope-extrapolated
lead). This is the classic Hilbert-phase SineWave: phase from a real
Hilbert transformer, sine = sin(phase), lead = sin(phase + 45 deg).
Ehlers' full HT_SINE additionally estimates the dominant cycle period
with a homodyne discriminator and smooths the phase; this build uses
the direct instantaneous phase of the FIR Hilbert transform instead
(see CALIBRATION.md).
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

CYCLE = 40        # detrender cycle length (bars)
N_TAPS = 51       # FIR Hilbert transformer length (odd)
GROUP_DELAY = (N_TAPS - 1) // 2  # 25 bars

INDICATOR_COLS = ["sine", "lead_sine", "phase", "atr"]


def _hilbert_taps(n_taps: int = N_TAPS) -> np.ndarray:
    """Hamming-windowed ideal Hilbert-transformer FIR coefficients.

    Tap k corresponds to lag n = k - (n_taps - 1) / 2. The ideal
    Hilbert impulse response is 2 / (pi*n) for odd n, 0 for even n.
    """
    centre = (n_taps - 1) // 2
    taps = np.zeros(n_taps)
    for k in range(n_taps):
        n = k - centre
        if n != 0 and n % 2 != 0:
            window = 0.54 - 0.46 * math.cos(2.0 * math.pi * k / (n_taps - 1))
            taps[k] = (2.0 / (math.pi * n)) * window
    return taps


def _high_pass(price: np.ndarray, cycle: int = CYCLE) -> np.ndarray:
    """Ehlers high-pass (roofing) detrender for the given cycle length."""
    alpha1 = (1.0 - math.sin(math.radians(360.0 / cycle))) / math.cos(
        math.radians(360.0 / cycle)
    )
    hp = np.zeros(len(price))
    a = (1.0 - alpha1 / 2.0) ** 2
    b = 2.0 * (1.0 - alpha1)
    c = (1.0 - alpha1) ** 2
    for i in range(2, len(price)):
        hp[i] = (
            a * (price[i] - 2.0 * price[i - 1] + price[i - 2])
            + b * hp[i - 1]
            - c * hp[i - 2]
        )
    return hp


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    price = ((df["h"] + df["l"]) / 2.0).to_numpy(dtype=float)
    n = len(price)
    d = _high_pass(price)

    taps = _hilbert_taps()
    # Q[i] = sum_k taps[k] * d[i-k]; np.convolve(d, taps)[i] is exactly
    # that sum (zero padding before bar 0, so only i >= 50 is a full
    # window). I[i] is the detrended price delayed by the group delay.
    q_full = np.convolve(d, taps, mode="full")[:n]
    in_phase = np.full(n, np.nan)
    if n > GROUP_DELAY:
        in_phase[GROUP_DELAY:] = d[: n - GROUP_DELAY]
    phase = np.full(n, np.nan)
    if n > N_TAPS - 1:
        phase[N_TAPS - 1:] = np.arctan2(
            q_full[N_TAPS - 1:], in_phase[N_TAPS - 1:]
        )
    df["phase"] = phase
    df["sine"] = np.sin(phase)
    df["lead_sine"] = np.sin(phase + math.pi / 4.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
