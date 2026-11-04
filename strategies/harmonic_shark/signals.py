"""Harmonic Shark signals: XABCD ratio match, entry at D confirmation.

Pivots alternate by construction (same-kind neighbours collapse to the
more extreme). A 5-pivot window X-A-B-C-D qualifies when its leg ratios
fall in the Shark bands; the entry fires at the D pivot's confirmation
bar (D index + 2, the pivot window lag). Bullish (XA up) -> long at D;
bearish (XA down) -> short at D. Exits are the opposite pattern's
completion plus the ATR stop / chandelier trail.
"""

import numpy as np
import pandas as pd

B_LO, B_HI = (0.332, 0.668)
C_LO, C_HI = (1.08, 1.668)
D_LO, D_HI = (0.836, 1.18)


def _pivots(df: pd.DataFrame):
    piv = []
    ph = df["pivot_high"].to_numpy()
    pl = df["pivot_low"].to_numpy()
    for i in range(len(df)):
        if not np.isnan(ph[i]):
            piv.append((i, "H", float(ph[i])))
        if not np.isnan(pl[i]):
            piv.append((i, "L", float(pl[i])))
    out = []
    for p in piv:
        if out and out[-1][1] == p[1] and out[-1][0] == p[0]:
            continue
        if out and out[-1][1] == p[1]:
            if p[1] == "H" and p[2] > out[-1][2]:
                out[-1] = p
            elif p[1] == "L" and p[2] < out[-1][2]:
                out[-1] = p
        else:
            out.append(p)
    return out


def _matches(x, a, b, c, d):
    xa = a - x
    ab = b - a
    bc = c - b
    cd = d - c
    if xa == 0 or ab == 0:
        return None
    if not ((xa > 0 and ab < 0 and bc > 0 and cd < 0) or
            (xa < 0 and ab > 0 and bc < 0 and cd > 0)):
        return None
    rb = abs(ab) / abs(xa)
    rc = abs(bc) / abs(ab)
    rd = abs(a - d) / abs(xa)
    if B_LO <= rb <= B_HI and C_LO <= rc <= C_HI and D_LO <= rd <= D_HI:
        return "long" if xa > 0 else "short"
    return None


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    piv = _pivots(df)
    for j in range(len(piv) - 4):
        w = piv[j:j + 5]
        kinds = "".join(p[1] for p in w)
        if kinds not in ("LHLHL", "HLHLH"):
            continue
        direction = _matches(w[0][2], w[1][2], w[2][2], w[3][2], w[4][2])
        if direction is None:
            continue
        confirm = w[4][0] + 2
        if confirm < n:
            if direction == "long":
                long_entry[confirm] = True
            else:
                short_entry[confirm] = True
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = short_entry.copy()
    df["short_exit"] = long_entry.copy()
    return df
