"""RSI with Bollinger Bands applied to RSI itself.

RSI(14) is itself an oscillator; putting Bollinger Bands around it
turns "RSI is stretched relative to its own recent history" into a
tradeable level. The bands adapt: in a trending market RSI rides one
band, in chop it oscillates between them.

Columns:
    rsi       -- Wilder RSI(14)
    rsi_mid   -- SMA(20) of RSI
    rsi_upper -- rsi_mid + 2 * std(20) of RSI
    rsi_lower -- rsi_mid - 2 * std(20) of RSI
    atr       -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import pandas as pd

from strategies import base as B

RSI_PERIOD = 14
BAND_PERIOD = 20
BAND_K = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    r = B.rsi(df["c"], RSI_PERIOD)
    mid = B.sma(r, BAND_PERIOD)
    sd = r.rolling(BAND_PERIOD, min_periods=BAND_PERIOD).std()
    df["rsi"] = r
    df["rsi_mid"] = mid
    df["rsi_upper"] = mid + BAND_K * sd
    df["rsi_lower"] = mid - BAND_K * sd
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
