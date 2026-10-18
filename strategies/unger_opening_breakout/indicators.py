"""Andrea Unger's championship opening-breakout indicators.

Unger's intraday systems trade the breakout of the first session range:
the high/low printed in the first two to three hours of the session become
the breakout levels. From the source interview: intraday breakout systems
use "the first two to three hours ... that session's high and low as
breakout levels with no take profit and a stop loss".

Implementation on 1h bars (session day = UTC day):
* range_high / range_low = high/low of the first 3 hourly bars of each UTC
  day (00:00, 01:00, 02:00 opens -- the 00:00-03:00 UTC window).
* A bar (from the 4th of the day onward) that CLOSES above range_high
  arms a long trigger; a close below range_low arms a short trigger.
* Only ONE trigger per side per day is kept: trigger columns are masked
  after the first trigger of each day per side.
* No lookahead: the range for day D is complete after bar 3 of day D, and
  only bars 4..24 can trigger.

Source: Andrea Unger interview (4x World Cup Trading Champion),
https://bettersystemtrader.com/016-andrea-unger/
"""

import numpy as np
import pandas as pd

from strategies import base as B

OPENING_BARS = 3  # first 3 hourly bars of the UTC day form the range


def add_indicators(
    df: pd.DataFrame, opening_bars: int = OPENING_BARS
) -> pd.DataFrame:
    df = df.copy()
    t = df["t"].to_numpy(dtype="int64")
    day = (t // 86_400_000).astype("int64")
    df["utc_day"] = day

    # position of each bar within its UTC day (0, 1, 2, ...)
    pos = np.zeros(len(df), dtype=np.int64)
    for d in np.unique(day):
        mask = day == d
        pos[mask] = np.arange(mask.sum())
    df["day_pos"] = pos

    # opening range: max/min over the first `opening_bars` bars of each day
    in_range = pos < opening_bars
    rh = pd.Series(np.nan, index=df.index, dtype=float)
    rl = pd.Series(np.nan, index=df.index, dtype=float)
    for d in np.unique(day):
        mask = (day == d) & in_range
        if mask.sum() >= opening_bars:  # full range only; partial days stay NaN
            tgt = day == d
            rh[tgt] = df["h"][mask].max()
            rl[tgt] = df["l"][mask].min()
    df["range_high"] = rh
    df["range_low"] = rl

    eligible = (pos >= opening_bars) & rh.notna() & rl.notna()
    raw_long = eligible & (df["c"] > df["range_high"])
    raw_short = eligible & (df["c"] < df["range_low"])
    # one trigger per side per day: keep only the first per (day, side)
    day_key = pd.Series(day, index=df.index)
    df["long_trigger"] = (
        raw_long & (raw_long.groupby(day_key).cumsum() == 1)
    ).fillna(False)
    df["short_trigger"] = (
        raw_short & (raw_short.groupby(day_key).cumsum() == 1)
    ).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
