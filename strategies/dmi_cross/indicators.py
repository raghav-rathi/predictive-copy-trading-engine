"""Wilder Directional Movement indicators (DMI / ADX), period 14.

Reuses strategies.base.adx, which implements Wilder smoothing
(ewm alpha = 1/14, the recursive form of Wilder's smoothing) for
+DM, -DM, True Range, and DX:

    +DM = h - prev_h when positive and larger than the -DM move, else 0
    -DM = prev_l - l when positive and larger than the +DM move, else 0
    +DI = 100 * smoothed(+DM) / smoothed(TR)
    -DI = 100 * smoothed(-DM) / smoothed(TR)
    DX  = 100 * |+DI - -DI| / (+DI + -DI)
    ADX = Wilder-smoothed DX

No new smoothing implementation is introduced here, so there is
no second, conflicting Wilder variant in the codebase.

Columns:
    adx      -- Wilder ADX(14), trend strength (0-100)
    plus_di  -- +DI(14)
    minus_di -- -DI(14)
    atr      -- Wilder ATR(14) for the risk layer

Causal: every value uses only bars through the current close.
ADX is first valid at bar 26 (DI needs 14 bars, DX needs DI,
ADX smoothing needs 14 DX values); earlier bars are NaN.
"""

import pandas as pd

from strategies import base as B

PERIOD = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dmi = B.adx(df["h"], df["l"], df["c"], PERIOD)
    df["adx"] = dmi["adx"]
    df["plus_di"] = dmi["plus_di"]
    df["minus_di"] = dmi["minus_di"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], PERIOD)
    return df
