"""Wilder Directional Movement indicators (ADX / +DI / -DI).

Classic J. Welles Wilder formulation from "New Concepts in Technical
Trading Systems" (1978):
    +DM = up-move when up-move > down-move and up-move > 0, else 0
    -DM = down-move when down-move > up-move and down-move > 0, else 0
    TR  = true range
    +DI = 100 * smoothed(+DM) / smoothed(TR)   (Wilder smoothing = alpha 1/n)
    -DI = 100 * smoothed(-DM) / smoothed(TR)
    DX  = 100 * |+DI - -DI| / (+DI + -DI)
    ADX = smoothed(DX) with the same Wilder smoothing
Default n=14. Everything is causal: only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

N = 14          # Wilder's classic period
ADX_ENTRY = 25  # ADX must be >= 25 for an entry to fire
ADX_FADE = 20   # ADX below 20 = trend faded (exit filter)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dm = B.adx(df["h"], df["l"], df["c"], N)
    df["plus_di"] = dm["plus_di"]
    df["minus_di"] = dm["minus_di"]
    df["adx"] = dm["adx"]
    df["di_spread"] = df["plus_di"] - df["minus_di"]
    return df
