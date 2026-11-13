"""Breaker block signals (ICT Smart Money Concepts).

A breaker forms when price closes THROUGH an order-block zone,
failing the block and flipping its polarity:

    failed bullish OB  -> BEARISH breaker: short on the retest,
        i.e. the first bar after a retest bar (a bar that closed
        back at/into the zone from below) that closes back below
        the zone low.
    failed bearish OB  -> BULLISH breaker: long on the retest,
        i.e. the first bar after a retest bar (a bar that closed
        back at/into the zone from above) that closes back above
        the zone high.

Only the most recent unmitigated breaker per direction is active;
a newer breaker of the same direction replaces an older one. A
breaker expires 200 bars after the break-through bar, is consumed
once traded, and is invalidated if price closes back through the
far side of the zone (above the high for a bearish breaker, below
the low for a bullish breaker).

Long exit:  the opposite (bearish-breaker) entry signal.
Short exit: the opposite (bullish-breaker) entry signal.
The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import numpy as np
import pandas as pd

EXPIRY_BARS = 200


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    bull_high = df["ob_bull_high"].to_numpy()
    bull_low = df["ob_bull_low"].to_numpy()
    bear_high = df["ob_bear_high"].to_numpy()
    bear_low = df["ob_bear_low"].to_numpy()

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    last_bull = None  # (high, low) of the most recently seen bull OB
    last_bear = None
    bear_breaker = None  # dict(low, high, break_bar, retested)
    bull_breaker = None

    for i in range(n):
        # Track the most recently seen order-block zones.
        if not np.isnan(bull_high[i]):
            last_bull = (bull_high[i], bull_low[i])
        if not np.isnan(bear_high[i]):
            last_bear = (bear_high[i], bear_low[i])

        # Break-through: the OB column cleared this bar while the
        # close is beyond the zone -> the breaker forms.
        if (np.isnan(bull_high[i]) and last_bull is not None and i > 0
                and not np.isnan(bull_high[i - 1])
                and c[i] < last_bull[1]):
            bear_breaker = {"low": last_bull[1], "high": last_bull[0],
                            "break_bar": i, "retested": False}
            last_bull = None
        if (np.isnan(bear_high[i]) and last_bear is not None and i > 0
                and not np.isnan(bear_high[i - 1])
                and c[i] > last_bear[0]):
            bull_breaker = {"low": last_bear[1], "high": last_bear[0],
                            "break_bar": i, "retested": False}
            last_bear = None

        # Bearish breaker (short on retest): expire, invalidate on a
        # close above the zone high, else track the retest and fire.
        if bear_breaker is not None:
            if i - bear_breaker["break_bar"] > EXPIRY_BARS:
                bear_breaker = None
            elif c[i] > bear_breaker["high"]:
                bear_breaker = None
            elif not bear_breaker["retested"]:
                if c[i] >= bear_breaker["low"]:
                    bear_breaker["retested"] = True
            elif c[i] < bear_breaker["low"]:
                short_entry[i] = True
                bear_breaker = None

        # Bullish breaker (long on retest): mirror image.
        if bull_breaker is not None:
            if i - bull_breaker["break_bar"] > EXPIRY_BARS:
                bull_breaker = None
            elif c[i] < bull_breaker["low"]:
                bull_breaker = None
            elif not bull_breaker["retested"]:
                if c[i] <= bull_breaker["high"]:
                    bull_breaker["retested"] = True
            elif c[i] > bull_breaker["high"]:
                long_entry[i] = True
                bull_breaker = None

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = short_entry.copy()
    df["short_exit"] = long_entry.copy()
    return df
