"""Wilder Volatility System indicators (J. Welles Wilder, 1978).

The Volatility System trades breakouts of the previous bar's range
expanded by one ATR:

    long trigger  = previous bar's high + ATR(7)
    short trigger = previous bar's low  - ATR(7)

ATR(7) is Wilder's ATR (shared strategies.base.atr primitive, Wilder
smoothing alpha = 1/7). The trigger levels are exposed as columns so
the signal logic is a plain comparison.

Columns:

    atr7               -- Wilder ATR(7)
    vol_long_trigger   -- h.shift(1) + atr7
    vol_short_trigger  -- l.shift(1) - atr7
    atr                -- Wilder ATR(14) for the risk layer

Distinct from strategies/wilder_volatility_stop, which is only the
trailing-stop component of Wilder's system. Here the ATR breakout
itself is the entry trigger.

No lookahead: ATR(7) on bar i uses data through bar i's close, and
the trigger uses the PREVIOUS bar's high/low, so everything on bar i
is known at bar i's close.
"""

import pandas as pd

from strategies import base as B

ATR_N = 7

INDICATOR_COLS = ["atr7", "vol_long_trigger", "vol_short_trigger", "atr"]


def add_indicators(df: pd.DataFrame, n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    df["atr7"] = B.atr(df["h"], df["l"], df["c"], n)
    df["vol_long_trigger"] = df["h"].shift(1) + df["atr7"]
    df["vol_short_trigger"] = df["l"].shift(1) - df["atr7"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
