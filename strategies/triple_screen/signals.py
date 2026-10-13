"""Triple Screen signals.

Screen 2 (wave): on 1h, FI2 crosses below 0 during a rising 4h tide (dip to
buy) / crosses above 0 during a falling tide (rally to sell).

Screen 3 (entry trigger): Elder uses a buy stop one tick above the prior
bar's high (sell stop below the prior bar's low). Approximated here: the
signal fires on bar i when bar i's high exceeds bar i-1's high (low undercuts
bar i-1's low for shorts); the harness then executes at bar i+1's open.
This is one bar later than a true stop fill — documented as an
approximation that biases results *against* the strategy, not for it.

Exits: the 4h tide flips (histogram slope crosses zero against the position)
or FI2 hooks back against the position (Elder's take-the-wave exit).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    zero = pd.Series(0.0, index=df.index)

    fi2_dip = B.crossed_below(df["fi2"], zero)
    fi2_pop = B.crossed_above(df["fi2"], zero)
    tide_up = df["tide_up"].fillna(False)
    tide_dn = df["tide_dn"].fillna(False)

    # Screen 2 + tide agreement; Screen 3: prior-bar high/low taken out
    armed_long = fi2_dip & tide_up
    armed_short = fi2_pop & tide_dn
    df["long_entry"] = armed_long & (df["h"] > df["h"].shift(1))
    df["short_entry"] = armed_short & (df["l"] < df["l"].shift(1))

    # Exits: tide flip or FI2 hook against the position
    df["long_exit"] = B.crossed_below(df["tide_slope"], zero) | fi2_pop
    df["short_exit"] = B.crossed_above(df["tide_slope"], zero) | fi2_dip

    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
