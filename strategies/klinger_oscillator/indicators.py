"""Stephen Klinger's Klinger Volume Oscillator (KVO) indicators.

Klinger ("Identifying Trends With Volume Analysis", Stocks & Commodities
1997) builds a signed "volume force" series and reads the difference of
two EMAs of it:

    hlc[i]  = H[i] + L[i] + C[i]
    trend   = +1 if hlc rises, -1 if it falls (else carries forward)
    dm[i]   = H[i] - L[i];  cm accumulates dm, resetting to dm[i-1] on a
              trend change
    VF[i]   = V[i] * |2*(dm[i]/cm) - 1| * 100 * trend[i]
    KVO     = EMA(VF, 34) - EMA(VF, 55)
    signal  = EMA(KVO, 13)

The dm/cm "temp" term scales volume force by how much of the recent
range the current bar accounts for. The cm accumulation is inherently
sequential, so this runs an explicit numpy loop (fast enough at 1h).
All causal: only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST = 34
SLOW = 55
SIGNAL = 13


def _volume_force(h, l, c, v):
    hlc = (h + l + c).to_numpy()
    dm = (h - l).to_numpy()
    vol = v.to_numpy()
    n = len(hlc)
    vf = np.zeros(n)
    trend = np.ones(n)
    cm = 0.0
    for i in range(n):
        if i == 0:
            t = 1.0
            cm = dm[0]
        else:
            if hlc[i] > hlc[i - 1]:
                t = 1.0
            elif hlc[i] < hlc[i - 1]:
                t = -1.0
            else:
                t = trend[i - 1]
            cm = dm[i - 1] + dm[i] if t != trend[i - 1] else cm + dm[i]
        trend[i] = t
        if cm != 0.0:
            vf[i] = vol[i] * abs(2.0 * (dm[i] / cm) - 1.0) * 100.0 * t
        # cm == 0 (degenerate flat bar) -> vf stays 0
    return pd.Series(vf, index=h.index)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vf = _volume_force(df["h"], df["l"], df["c"], df["v"])
    df["kvo"] = B.ema(vf, FAST) - B.ema(vf, SLOW)
    df["kvo_signal"] = B.ema(df["kvo"], SIGNAL)
    return df
