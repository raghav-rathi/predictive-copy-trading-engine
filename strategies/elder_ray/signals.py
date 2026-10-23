"""Elder Ray signals -- buy-the-dip / sell-the-rip around EMA(13).

Long (dip in an uptrend, bears losing grip):

    long_entry = (ema13 slope up)
             AND (bear_power < 0)          -- bears still in control of the bar's low
             AND (bear_power rising)       -- but weakening (higher than prior bar)

Short (mirror -- rip in a downtrend, bulls losing grip):

    short_entry = (ema13 slope down)
              AND (bull_power > 0)
              AND (bull_power falling)

Exits -- momentum-mature or trend lost:

    long_exit  = bear_power crosses ABOVE 0 (bears exhausted, the dip is over)
             OR ema13 slope turns down (uptrend structure broken)
    short_exit = bull_power crosses BELOW 0
             OR ema13 slope turns up

Slope comparisons use .shift(1) on the ema13 series itself; the crosses
use the bar-i level against the shifted level, so the signal on bar i
uses only data through bar i's close. The harness executes at bar i+1's
open.

Signal columns are boolean, no NaN.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

ZERO = 0.0


def _b(s: pd.Series) -> pd.Series:
    """Boolean series, no NaN."""
    return s.fillna(False).astype(bool)


def _zero(s: pd.Series) -> pd.Series:
    return pd.Series(0.0, index=s.index)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ema13 = df["ema13"]
    bull = df["bull_power"]
    bear = df["bear_power"]

    ema_up = _b(ema13 > ema13.shift(1))
    ema_down = _b(ema13 < ema13.shift(1))
    bear_rising = _b(bear > bear.shift(1))
    bull_falling = _b(bull < bull.shift(1))

    df["long_entry"] = (ema_up & (bear < ZERO) & bear_rising).astype(bool)
    df["short_entry"] = (ema_down & (bull > ZERO) & bull_falling).astype(bool)

    bear_exhausted = crossed_above(bear, _zero(bear)).fillna(False)
    bull_exhausted = crossed_below(bull, _zero(bull)).fillna(False)
    df["long_exit"] = (bear_exhausted | ema_down).astype(bool)
    df["short_exit"] = (bull_exhausted | ema_up).astype(bool)
    return df
