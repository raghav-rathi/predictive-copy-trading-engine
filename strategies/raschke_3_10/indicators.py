"""Linda Raschke's 3/10 oscillator indicators (Raschke & Connors,
"Street Smarts", 1995).

median = (h + l) / 2
osc    = SMA(median, 3) - SMA(median, 10)
signal = SMA(osc, 16)

The 3/10 is a MACD-style momentum oscillator on the median price; the
16-bar SMA of the oscillator is the trigger line.  No lookahead: every
value on bar i uses bars through i only.
"""

import pandas as pd

from strategies import base as B

FAST = 3
SLOW = 10
SIGNAL = 16


def add_indicators(
    df: pd.DataFrame,
    fast: int = FAST,
    slow: int = SLOW,
    signal: int = SIGNAL,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    osc = B.sma(median, fast) - B.sma(median, slow)
    df["osc_3_10"] = osc
    df["osc_3_10_signal"] = B.sma(osc, signal)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
