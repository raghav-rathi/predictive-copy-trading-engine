"""Wilder RSI(14) against its own SMA(14) signal line.

RSI is Wilder's (StockCharts definition): average gain / average
loss smoothed with Wilder's alpha = 1/14, RSI = 100 - 100/(1+RS),
shared via strategies.base.rsi so every RSI strategy in the
library computes the identical series. The signal line is a plain
14-bar simple moving average of the RSI itself — the classic
"RSI vs its moving average" crossover setup, not an overbought /
oversold level trade: the cross, not the level, is the signal.

All windows are trailing (min_periods=n); no lookahead.

Columns:

    rsi     -- Wilder RSI(14), in [0, 100]
    rsi_sma -- SMA(rsi, 14)
    atr     -- Wilder ATR(14) for the risk layer
"""

import pandas as pd

from strategies import base as B

RSI_N = 14       # Wilder RSI length (fixed a priori)
SIGNAL_N = 14    # signal-line SMA length (fixed a priori)


def add_indicators(df: pd.DataFrame, n: int = RSI_N,
                   signal_n: int = SIGNAL_N) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], n)
    df["rsi_sma"] = (
        df["rsi"].rolling(signal_n, min_periods=signal_n).mean()
    ).ffill().bfill()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
