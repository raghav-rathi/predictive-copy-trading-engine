"""Ehlers MESA Sine Wave indicators (John Ehlers, "Cycle Analytics
for Traders" / "Rocket Science for Traders" ch. 12).

Pipeline (all causal, no lookahead):

    hl2    = (h + l) / 2
    smooth = 4-bar WMA: (4*hl2 + 3*hl2[1] + 2*hl2[2] + hl2[3]) / 10
    detrender = Hilbert filter on smooth:
        (0.0962*x + 0.5769*x[2] - 0.5769*x[4] - 0.0962*x[6])
        * (0.075 * Period[1] + 0.54)
    I1 = detrender[3]                      (in-phase, lagged 3 bars)
    Q1 = same Hilbert filter on detrender  (quadrature)
    jI = same Hilbert filter on I1;  jQ = same Hilbert filter on Q1
    I2 = I1 - jQ;  Q2 = Q1 + jI, each then smoothed 0.2/0.8
    phase = atan2(Q2, I2)
    Period via the homodyne discriminator:
        Re = I2*I2[1] + Q2*Q2[1];  Im = I2*Q2[1] - Q2*I2[1]
        dphi = atan2(Im, Re);  raw Period = 2*pi / dphi
        (Ehlers' original uses arctan(Im/Re); atan2 is the same
        discriminator with correct quadrants)
        rate-limited to [0.67x, 1.5x] of the previous period,
        clamped to [6, 50], smoothed 0.2/0.8
    sine = sin(phase);  lead_sine = sin(phase + pi/4)

The (0.075*Period[1] + 0.54) factor uses the previous bar's
period, never the current one, so every value on bar i uses
data through bar i's close only.

Columns:
    mesa_sine       -- sin(phase)
    mesa_lead_sine  -- sin(phase + pi/4), leads sine by 45 degrees
    mesa_phase      -- cycle phase in radians
    mesa_period     -- dominant cycle period, bars, clamped 6..50
    mesa_i2, mesa_q2 -- smoothed in-phase / quadrature components
    atr             -- ATR(14) for the harness
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

SMOOTH = 0.2        # shipped I2/Q2 smoothing factor (sweep knob)
PERIOD_INIT = 20.0
PERIOD_MIN = 6.0
PERIOD_MAX = 50.0


def _hilbert(arr, i: int, period_prev: float) -> float:
    return (
        0.0962 * arr[i]
        + 0.5769 * arr[i - 2]
        - 0.5769 * arr[i - 4]
        - 0.0962 * arr[i - 6]
    ) * (0.075 * period_prev + 0.54)


def add_indicators(df: pd.DataFrame, smooth: float = SMOOTH) -> pd.DataFrame:
    df = df.copy()
    hl2 = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    n = len(hl2)
    sm = np.full(n, np.nan)
    det = np.full(n, np.nan)
    i1 = np.full(n, np.nan)
    q1 = np.full(n, np.nan)
    ji = np.full(n, np.nan)
    jq = np.full(n, np.nan)
    i2 = np.full(n, np.nan)
    q2 = np.full(n, np.nan)
    period = np.full(n, PERIOD_INIT)
    phase = np.full(n, np.nan)
    sine = np.full(n, np.nan)
    lead = np.full(n, np.nan)

    def fin(a, k):
        return 0 <= k < n and np.isfinite(a[k])

    for i in range(n):
        per_prev = period[i - 1] if i > 0 else PERIOD_INIT
        if i >= 3 and all(fin(hl2, i - k) for k in range(4)):
            sm[i] = (4 * hl2[i] + 3 * hl2[i - 1] + 2 * hl2[i - 2] + hl2[i - 3]) / 10.0
        if i >= 9 and all(fin(sm, i - k) for k in (0, 2, 4, 6)):
            det[i] = _hilbert(sm, i, per_prev)
        if i >= 12 and fin(det, i - 3):
            i1[i] = det[i - 3]
        if i >= 15 and all(fin(det, i - k) for k in (0, 2, 4, 6)):
            q1[i] = _hilbert(det, i, per_prev)
        if i >= 18 and all(fin(i1, i - k) for k in (0, 2, 4, 6)):
            ji[i] = _hilbert(i1, i, per_prev)
        if i >= 21 and all(fin(q1, i - k) for k in (0, 2, 4, 6)):
            jq[i] = _hilbert(q1, i, per_prev)
        if i >= 21 and all(fin(a, i) for a in (i1, q1, ji, jq)):
            i2_raw = i1[i] - jq[i]
            q2_raw = q1[i] + ji[i]
            prev_i2 = i2[i - 1] if fin(i2, i - 1) else i2_raw
            prev_q2 = q2[i - 1] if fin(q2, i - 1) else q2_raw
            i2[i] = smooth * i2_raw + (1.0 - smooth) * prev_i2
            q2[i] = smooth * q2_raw + (1.0 - smooth) * prev_q2
        # homodyne discriminator on the smoothed components
        if i > 0 and all(fin(a, i) for a in (i2, q2)) and all(fin(a, i - 1) for a in (i2, q2)):
            re = i2[i] * i2[i - 1] + q2[i] * q2[i - 1]
            im = i2[i] * q2[i - 1] - q2[i] * i2[i - 1]
            dphi = math.atan2(im, re)
            if dphi > 1e-9:
                raw = 2.0 * math.pi / dphi
                raw = min(max(raw, 0.67 * per_prev), 1.5 * per_prev)
                raw = min(max(raw, PERIOD_MIN), PERIOD_MAX)
                period[i] = 0.2 * raw + 0.8 * per_prev
            else:
                period[i] = per_prev
        else:
            period[i] = per_prev
        if np.isfinite(i2[i]) and np.isfinite(q2[i]):
            phase[i] = math.atan2(q2[i], i2[i])
            sine[i] = math.sin(phase[i])
            lead[i] = math.sin(phase[i] + math.pi / 4.0)

    df["mesa_sine"] = sine
    df["mesa_lead_sine"] = lead
    df["mesa_phase"] = phase
    df["mesa_period"] = period
    df["mesa_i2"] = i2
    df["mesa_q2"] = q2
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
