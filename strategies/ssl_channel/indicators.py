"""SSL Channel indicators.

The SSL (Semaphor / "SSL Channel") is a two-line channel:
    ssl_up = SMA(High, n)
    ssl_dn = SMA(Low,  n)

Bullish regime: close > ssl_up. Bearish regime: close < ssl_dn.
Between the lines the prior regime persists (state machine resolved
in signals.py).

No lookahead: SMA on bar i uses data through i only.
"""

import pandas as pd

from strategies import base as B

SSL_LEN = 10
ATR_N = 14


def add_indicators(df: pd.DataFrame, n: int = SSL_LEN) -> pd.DataFrame:
    df = df.copy()
    df["ssl_up"] = B.sma(df["h"], n)
    df["ssl_dn"] = B.sma(df["l"], n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
