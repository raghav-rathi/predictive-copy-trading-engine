"""Wyckoff distribution signals (SHORT ONLY).

Short entry: on the UTAD-reclaim bar's close, OR on an LPSY
bar after an SOW. Both are single-fire state-machine events
(see indicators.py), not persistent level conditions, so an
entry fires on exactly one bar per setup.

Exit: the close rises above utad_high (invalidation -- the
UTAD failed) OR the close falls below the cause-effect range
projection range_low - 1.0x (range_high - range_low) (the
projected cause is reached). Both levels are frozen at the
entry bar (causal: values known at the entry close). The
house 2xATR hard stop / 3xATR trail sit behind these exits,
and the 120-bar max hold caps a schematic that never
resolves.

No longs: distribution is a bearish schematic; the mirror
accumulation setup is a different strategy.

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
    utad_high = df["utad_high"].to_numpy(float)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = (
        (df["utad"].fillna(False) | df["lpsy"].fillna(False))
        .to_numpy(bool)
    )

    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    held_utad_high = None  # utad_high frozen at the entry bar
    held_target = None     # range projection frozen at the entry bar
    for i in range(n):
        # Exits are judged against levels from entries on earlier bars.
        if held_utad_high is not None and (
            c[i] > held_utad_high
            or (held_target is not None and c[i] < held_target)
        ):
            short_exit[i] = True
            held_utad_high = None
            held_target = None
        if held_utad_high is None and short_entry[i]:
            held_utad_high = utad_high[i]
            if not np.isnan(rh[i]) and not np.isnan(rl[i]):
                held_target = rl[i] - 1.0 * (rh[i] - rl[i])
            else:
                held_target = None
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
