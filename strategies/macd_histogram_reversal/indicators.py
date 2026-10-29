"""Elder MACD-histogram indicators.

MACD = EMA(12) - EMA(26), signal = EMA(9) of the MACD line, from
strategies.base.macd. The histogram is the difference between
the two: the slope of the histogram is the second derivative of
price momentum, and Alexander Elder's rule trades its slope
flips — a histogram that stops falling and ticks up marks
bullish momentum turning even while the MACD line itself is
still below its signal, and vice versa.

Columns:
    macd        -- MACD line (EMA12 - EMA26)
    macd_signal -- EMA(9) of the MACD line
    macd_hist   -- macd - macd_signal (the Elder histogram)
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every window is trailing (min_periods=n); the
histogram at bar i uses only closes through bar i.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], FAST, SLOW, SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
