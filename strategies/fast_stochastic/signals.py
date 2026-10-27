"""Fast Stochastic signals: cross in the zone, exit on the opposite
cross. %D (not %K) carries the zone condition because %D lags and is
still in the zone when %K hooks back.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = crossed_above(df["stoch_k"], df["stoch_d"]) & (df["stoch_d"] < 20)
    dn = crossed_below(df["stoch_k"], df["stoch_d"]) & (df["stoch_d"] > 80)
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = dn.fillna(False).astype(bool)
    df["long_exit"] = dn.fillna(False).astype(bool)
    df["short_exit"] = up.fillna(False).astype(bool)
    return df
