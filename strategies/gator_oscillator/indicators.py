"""Gator Oscillator indicators -- convergence/divergence degree of the
Alligator's three balance lines (Bill Williams).

Balance lines on median price (h+l)/2, all Wilder-smoothed (SMMA) and
forward-displaced with .shift(k) (uses past data only, no lookahead):

    jaw   = SMMA(median, 13) shifted 8 bars
    teeth = SMMA(median, 8)  shifted 5 bars
    lips  = SMMA(median, 5)  shifted 3 bars

The Gator Oscillator plots two histograms around zero:

    gator_upper =  |jaw - teeth|     (plotted above zero)
    gator_lower = -|teeth - lips|    (plotted below zero)

Each bar is green when its absolute value is rising vs the prior bar
(the Alligator is opening its mouth / eating) and red otherwise (the
mouth is closing / the Alligator sleeps). Fan order gives direction:

    fan_bull = lips > teeth > jaw    (mouth open upward)
    fan_bear = lips < teeth < jaw    (mouth open downward)

Columns:

    alligator_jaw, alligator_teeth, alligator_lips
    gator_upper, gator_lower            -- the two histograms
    gator_upper_green, gator_lower_green -- bar-to-bar color
    gator_eats     -- both histograms green (expanding)
    gator_sleeps   -- both histograms red (contracting)
    fan_bull, fan_bear
    atr                            -- Wilder ATR(14) for the risk layer

No lookahead: every series on bar j uses data through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

JAW_LEN = 13    # shipped default (Bill Williams' canonical value)
TEETH_LEN = 8
LIPS_LEN = 5
JAW_SHIFT = 8
TEETH_SHIFT = 5
LIPS_SHIFT = 3


def smma(s: pd.Series, n: int) -> pd.Series:
    """Wilder-style smoothed moving average.

    Recursive form: smma[i] = (smma[i-1]*(n-1) + x[i]) / n.
    ewm(alpha=1/n, adjust=False) is exactly that recursion, seeded with
    y[0] = x[0]; min_periods=n keeps the spin-up honest.
    """
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def scaled_params(jaw_len: int):
    """Scale Bill Williams' 13/8/5 lengths and 8/5/3 shifts by jaw_len,
    keeping the 13:8:5 and 8:5:3 ratios (rounded to whole bars)."""
    return (
        int(round(jaw_len * 8 / 13)),   # teeth length
        int(round(jaw_len * 5 / 13)),   # lips length
        int(round(jaw_len * 8 / 13)),   # jaw shift
        int(round(jaw_len * 5 / 13)),   # teeth shift
        int(round(jaw_len * 3 / 13)),   # lips shift
    )


def add_indicators(df: pd.DataFrame,
                   jaw_len: int = JAW_LEN,
                   teeth_len: int = TEETH_LEN,
                   lips_len: int = LIPS_LEN,
                   jaw_shift: int = JAW_SHIFT,
                   teeth_shift: int = TEETH_SHIFT,
                   lips_shift: int = LIPS_SHIFT) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2

    jaw = smma(median, jaw_len).shift(jaw_shift)
    teeth = smma(median, teeth_len).shift(teeth_shift)
    lips = smma(median, lips_len).shift(lips_shift)

    df["alligator_jaw"] = jaw
    df["alligator_teeth"] = teeth
    df["alligator_lips"] = lips

    upper = (jaw - teeth).abs()
    lower = -(teeth - lips).abs()
    df["gator_upper"] = upper
    df["gator_lower"] = lower

    # Green when the bar's absolute value is rising vs the prior bar.
    # |lower| rises when the (negative) lower value falls.
    upper_green = (upper.diff() > 0).fillna(False)
    lower_green = (lower.diff() < 0).fillna(False)
    df["gator_upper_green"] = upper_green
    df["gator_lower_green"] = lower_green

    df["gator_eats"] = (upper_green & lower_green).fillna(False)
    df["gator_sleeps"] = ((~upper_green) & (~lower_green)).fillna(False)

    fan_bull = (lips > teeth) & (teeth > jaw)
    fan_bear = (lips < teeth) & (teeth < jaw)
    df["fan_bull"] = fan_bull.fillna(False)
    df["fan_bear"] = fan_bear.fillna(False)

    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
