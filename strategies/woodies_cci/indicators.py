"""Woodies CCI indicators (Ken Wood).

The Commodity Channel Index measures how far the typical price has
deviated from its mean, in units of mean absolute deviation scaled
by Lambert's 0.015 constant:

    tp       = (h + l + c) / 3
    CCI(n)   = (tp - SMA(tp, n)) / (0.015 * mean(|tp - SMA(tp, n)|))

Two CCIs run side by side, exactly as in Wood's system:
    cci14  -- the trend line: which side of the zero line it's on
              (and for how long) defines the tradable direction
    turbo  -- the fast CCI(6) trigger: its hook back through the zero
              line times the pullback entry

The 0/0 case (typical price flat over the window, mean deviation =
0) is guarded: CCI is pinned to 0 (i.e. exactly at the zero line)
rather than NaN, keeping the frame clean without inventing a side.

Columns:
    tp     -- typical price
    cci14  -- trend CCI(14)
    turbo  -- fast CCI(6)

No lookahead: the value on bar j uses data through bar j's close
only (rolling windows with min_periods=n).
"""

import numpy as np
import pandas as pd

from strategies import base as B

TREND_N = 14  # shipped default
TURBO_N = 6   # shipped default


def cci(tp: pd.Series, n: int) -> pd.Series:
    """CCI(n) of a typical-price series with a 0/0 guard (flat -> 0)."""
    ma = B.sma(tp, n)
    mean_dev = (tp - ma).abs().rolling(n, min_periods=n).mean()
    denom = 0.015 * mean_dev
    out = (tp - ma) / denom
    # flat window (denominator 0 but window fully formed) -> sit at zero line
    flat = (denom == 0) & denom.notna()
    return out.where(~flat, 0.0)


def add_indicators(
    df: pd.DataFrame,
    trend_n: int = TREND_N,
    turbo_n: int = TURBO_N,
) -> pd.DataFrame:
    df = df.copy()
    df["tp"] = (df["h"] + df["l"] + df["c"]) / 3.0
    df["cci14"] = cci(df["tp"], trend_n)
    df["turbo"] = cci(df["tp"], turbo_n)
    return df
