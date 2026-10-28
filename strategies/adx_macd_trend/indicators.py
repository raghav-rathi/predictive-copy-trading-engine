"""ADX + MACD trend filter (Wilder DMI + Appel MACD).

Long requires trend strength AND trend direction AND momentum timing
to agree: ADX(14) > 25, +DI > -DI, and the MACD line crossing above
its signal line. Short is the mirror. The ADX gate keeps the strategy
out of range-bound chop where MACD crosses whipsaw; the DI filter
keeps entries on the side of the prevailing trend.

Columns:
    adx, plus_di, minus_di -- Wilder DMI(14) via strategies.base.adx
    macd, macd_signal, macd_hist -- MACD(12, 26, 9)
    atr -- Wilder ATR(14) for the risk layer

All indicators are causal (EMA/Wilder smoothing reads bars <= i only).
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dmi = B.adx(df["h"], df["l"], df["c"], 14)
    df["adx"] = dmi["adx"]
    df["plus_di"] = dmi["plus_di"]
    df["minus_di"] = dmi["minus_di"]
    m = B.macd(df["c"], 12, 26, 9)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
