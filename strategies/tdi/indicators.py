"""Traders Dynamic Index indicators (Dean Malone, CompassFX, 2007).

green = RSI(13) of close                (RSI Price Line)
red   = SMA(green, 2)                   (Trade Signal Line)
yellow= SMA(green, 34)                  (Market Base Line)
bands = Bollinger(green, 34, 1.6185)    (Volatility Bands, golden-ratio width)
All causal: only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

RSI_N = 13
TSL_N = 2
MBL_N = 34
VB_N = 34
VB_K = 1.6185


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    green = B.rsi(df["c"], RSI_N)
    red = B.sma(green, TSL_N)
    yellow = B.sma(green, MBL_N)
    mid = B.sma(green, VB_N)
    sd = green.rolling(VB_N, min_periods=VB_N).std()
    df["tdi_green"] = green
    df["tdi_red"] = red
    df["tdi_yellow"] = yellow
    df["tdi_vb_up"] = mid + VB_K * sd
    df["tdi_vb_dn"] = mid - VB_K * sd
    return df
