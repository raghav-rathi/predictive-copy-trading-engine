"""Weis Wave signals.

Long: a new up-wave starts (wave_dir flips -1 -> +1, i.e. the previous
down-wave ended by reversal) AND the just-completed down-wave's volume
was less than 85% of the completed up-wave before it — selling effort
drying up into the turn.
Short: mirror — a new down-wave starts AND the just-completed up-wave's
volume was less than 85% of the completed down-wave before it.

Exits: long exits on the start of a new down-wave (wave_dir flips to
-1); short exits on the start of a new up-wave. The ATR stop / trail in
the risk layer also applies.

All inputs are computed from data through bar i's close, so signals on
bar i use no future data.
"""

import pandas as pd

from strategies.weis_wave.indicators import VOLUME_RATIO


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_dir = df["wave_dir"].shift(1)
    start_up = (df["wave_dir"] == 1) & (prev_dir == -1)
    start_down = (df["wave_dir"] == -1) & (prev_dir == 1)
    vol_dry_long = df["last_completed_wave_vol"] < VOLUME_RATIO * df["prev_completed_wave_vol"]
    vol_dry_short = df["last_completed_wave_vol"] < VOLUME_RATIO * df["prev_completed_wave_vol"]
    df["long_entry"] = (start_up & vol_dry_long).fillna(False).astype(bool)
    df["short_entry"] = (start_down & vol_dry_short).fillna(False).astype(bool)
    df["long_exit"] = start_down.fillna(False).astype(bool)
    df["short_exit"] = start_up.fillna(False).astype(bool)
    return df
