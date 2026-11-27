"""Wyckoff accumulation signals (LONG ONLY).

Long entry: on the spring-reclaim bar's close, OR on an LPS
bar after an SOS. Both are single-fire state-machine events
(see indicators.py), not persistent level conditions, so an
entry fires on exactly one bar per setup.

Exit: the close falls below spring_low (invalidation -- the
spring failed) OR the close rises above the cause-effect
range projection range_high + 1.0x (range_high - range_low)
(the projected cause is reached). Both levels are frozen at
the entry bar (causal: values known at the entry close).
The house 2xATR hard stop / 3xATR trail sit behind these
exits, and the 240-bar max hold caps a schematic that never
resolves.

No shorts: accumulation is a bullish schematic; the mirror
distribution setup is a different strategy.

Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(float)
    rh = df["range_high_120"].to_numpy(float)
    rl = df["range_low_120"].to_numpy(float)
    spring_low = df["spring_low"].to_numpy(float)
    long_entry = (
        (df["spring"].fillna(False) | df["lps"].fillna(False))
        .to_numpy(bool)
    )
    short_entry = np.zeros(n, dtype=bool)

    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    held_spring_low = None  # spring_low frozen at the entry bar
    held_target = None      # range projection frozen at the entry bar
    for i in range(n):
        # Exits are judged against levels from entries on earlier bars.
        if held_spring_low is not None and (
            c[i] < held_spring_low
            or (held_target is not None and c[i] > held_target)
        ):
            long_exit[i] = True
            held_spring_low = None
            held_target = None
        if held_spring_low is None and long_entry[i]:
            held_spring_low = spring_low[i]
            if not np.isnan(rh[i]) and not np.isnan(rl[i]):
                held_target = rh[i] + 1.0 * (rh[i] - rl[i])
            else:
                held_target = None
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
