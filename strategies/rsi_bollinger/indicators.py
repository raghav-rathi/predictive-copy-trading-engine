"""Bollinger Bands on RSI indicators (mean-reversion system).

Instead of banding price, this bands the RSI(14) itself with 20-period
Bollinger Bands (2 std). Tags of the outer bands mark momentum
exhaustion: RSI stretched below its lower band is an oversold extreme,
above its upper band an overbought extreme. Entries trigger when RSI
re-enters the bands (exhaustion confirmed); exits at the band midline
(mean reversion complete). All causal: only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

RSI_N = 14
BB_N = 20
BB_K = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], RSI_N)
    mid = B.sma(rsi, BB_N)
    sd = rsi.rolling(BB_N, min_periods=BB_N).std()
    df["rsi"] = rsi
    df["rsi_bb_mid"] = mid
    df["rsi_bb_upper"] = mid + BB_K * sd
    df["rsi_bb_lower"] = mid - BB_K * sd
    return df
