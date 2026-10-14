"""Floor-trader pivot point indicators (classic R1/S1 breakout).

For each UTC day of 1h bars (24 bars), levels are computed from the prior
COMPLETE day's OHLC:

    PP = (H + L + C) / 3
    R1 = 2*PP - L        S1 = 2*PP - H
    R2 = PP + (H - L)    S2 = PP - (H - L)

The prior-day levels are forward-filled within the current day, so every
bar carries the levels set at its own day's open -- no intraday
recalculation, no lookahead. Days with fewer than 24 bars (partial first
day in the cache, DST-free UTC so always 24) poison the levels to NaN
rather than biasing the breakout line. 24/7 crypto has no overnight gaps,
so the break-and-close rule suffices without a gap filter.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BARS_PER_DAY = 24
MS_PER_DAY = 86_400_000


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    day = pd.Series((df["t"] // MS_PER_DAY).to_numpy(), index=df.index)

    agg = pd.DataFrame(
        {
            "h": df.groupby(day)["h"].max(),
            "l": df.groupby(day)["l"].min(),
            "c": df.groupby(day)["c"].last(),
            "n": df.groupby(day)["c"].size(),
        }
    ).sort_index()
    complete = agg["n"] >= BARS_PER_DAY
    ph = agg["h"].where(complete).shift(1)
    pl = agg["l"].where(complete).shift(1)
    pc = agg["c"].where(complete).shift(1)
    pp = (ph + pl + pc) / 3.0
    r1 = 2.0 * pp - pl
    s1 = 2.0 * pp - ph
    r2 = pp + (ph - pl)
    s2 = pp - (ph - pl)

    levels = pd.DataFrame({"pp": pp, "r1": r1, "s1": s1, "r2": r2, "s2": s2})
    for col in levels.columns:
        df[col] = day.map(levels[col]).to_numpy(dtype=float)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
