"""Balance of Power -- buyer-vs-seller control gauge (Igor Livshin, S&C Aug 2001).

    raw_bop = (close - open) / (high - low)      (0.0 when high == low)
    bop     = SMA(raw_bop, n)

Raw BOP is bounded in [-1, +1] per bar: +1 means buyers owned the
whole bar (opened at the low, closed at the high), -1 means sellers
did. The SMA(n) version smooths the bar-by-bar chop into a regime
read: sustained positive BOP = buyers in control (an up-trend leg),
sustained negative = sellers in control.

The zero line is the control threshold — who won the recent bars.
Columns:

    raw_bop -- unsmoothed per-bar balance of power, in [-1, +1]
    bop     -- SMA(raw_bop, n), the tradable regime line
    atr     -- Wilder ATR(14) for the risk layer

No lookahead: SMA on bar j uses data through bar j only
(rolling(min_periods=n)).
"""

import numpy as np
import pandas as pd

from strategies import base as B

BOP_LEN = 14  # shipped default (StockCharts default smoothing)


def raw_bop(o: pd.Series, h: pd.Series, l: pd.Series,
            c: pd.Series) -> pd.Series:
    """Per-bar balance of power in [-1, +1].

    +1: opened at the low, closed at the high (buyers won the bar).
    -1: opened at the high, closed at the low (sellers won the bar).
    0.0 when high == low (degenerate bar, no range to split).
    """
    rng = (h - l).replace(0.0, np.nan)
    val = (c - o) / rng
    return val.fillna(0.0)


def balance_of_power(o: pd.Series, h: pd.Series, l: pd.Series,
                     c: pd.Series, n: int = BOP_LEN) -> pd.DataFrame:
    """Raw BOP plus its SMA(n) smoothing."""
    raw = raw_bop(o, h, l, c)
    return pd.DataFrame({"raw_bop": raw, "bop": B.sma(raw, n)})


def add_indicators(df: pd.DataFrame, n: int = BOP_LEN) -> pd.DataFrame:
    df = df.copy()
    b = balance_of_power(df["o"], df["h"], df["l"], df["c"], n)
    df["raw_bop"] = b["raw_bop"]
    df["bop"] = b["bop"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
