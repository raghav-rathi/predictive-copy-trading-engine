"""Accelerator Oscillator (AC) -- Bill Williams, New Trading Dimensions.

    med = (high + low) / 2            -- median price
    ao  = SMA(med, fast) - SMA(med, slow)   -- Awesome Oscillator
    ac  = ao - SMA(ao, signal)         -- Accelerator Oscillator

AC is the acceleration of momentum: it measures how the driving force
(AO) is changing bar to bar. A bar is GREEN when ac[j] > ac[j-1]
(acceleration rising) and RED when ac[j] < ac[j-1]; a flat bar
(ac[j] == ac[j-1]) is neither and breaks a color run. The COLOR is the
bar-to-bar change, not the level: a rising bar below the zero line is
green, a falling bar above the zero line is red. The zero line itself
is never a signal -- only the color sequence matters.

Columns:

    med       -- median price (high + low) / 2
    ao        -- Awesome Oscillator, SMA(med, fast) - SMA(med, slow)
    ac        -- Accelerator Oscillator, ao - SMA(ao, signal)
    ac_green  -- True when ac[j] > ac[j-1] (green bar), else False
    ac_red    -- True when ac[j] < ac[j-1] (red bar), else False
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: every SMA on bar j uses data through bar j only;
rolling(min_periods=n) means ao's first fully-formed value arrives
after slow-1 bars, and ac after another signal-1.
"""

import pandas as pd

from strategies import base as B

FAST = 5    # shipped default (Williams' AO fast leg)
SLOW = 34   # shipped default (Williams' AO slow leg)
SIGNAL = 5  # shipped default (Williams' AC smoothing)


def awesome(med: pd.Series, fast: int = FAST, slow: int = SLOW) -> pd.Series:
    """Awesome Oscillator: SMA(med, fast) - SMA(med, slow)."""
    return B.sma(med, fast) - B.sma(med, slow)


def accelerator(ao: pd.Series, signal: int = SIGNAL) -> pd.Series:
    """Accelerator Oscillator: ao - SMA(ao, signal)."""
    return ao - B.sma(ao, signal)


def add_indicators(df: pd.DataFrame, fast: int = FAST, slow: int = SLOW,
                   signal: int = SIGNAL) -> pd.DataFrame:
    df = df.copy()
    med = (df["h"] + df["l"]) / 2.0
    ao = awesome(med, fast, slow)
    ac = accelerator(ao, signal)
    df["med"] = med
    df["ao"] = ao
    df["ac"] = ac
    # Color = bar-to-bar change of ac, not its level. NaN comparisons
    # evaluate to False in pandas, so warmup bars stay colorless
    # (neither green nor red) and break color runs.
    df["ac_green"] = (ac > ac.shift(1)).astype(bool)
    df["ac_red"] = (ac < ac.shift(1)).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
