"""Raschke "Anti" signals.

Arming (long): %D-slope uptrend AND a counter-move (fast %K hooks down
through %D, or a 2-bar inside day). The armed state persists
``arm_window`` bars.
Entry (long): armed on a prior bar AND momentum re-aligns now --
fast %K turns back up through %D, OR 3/10 crosses back above its
16-signal -- still in the uptrend.
Exit: opposite setup (3/10 crosses against, or %K hooks against while
%D slopes against the position). Chandelier trailing stop in risk.py.

Mirror for shorts. Parameterizable arm_window for calibration.
"""

import pandas as pd

from strategies import base as B
from strategies.raschke_anti.indicators import ARM_WINDOW


def _armed(raw: pd.Series, arm_window: int) -> pd.Series:
    """Persistence of the arming condition over the last arm_window bars."""
    return (raw.fillna(False).rolling(arm_window, min_periods=1).max() > 0)


def add_signals(df: pd.DataFrame, arm_window: int = ARM_WINDOW) -> pd.DataFrame:
    df = df.copy()
    arm_long_raw = df["uptrend"] & (df["hook_dn"] | df["inside2"])
    arm_short_raw = df["downtrend"] & (df["hook_up"] | df["inside2"])
    arm_long = _armed(arm_long_raw, arm_window).shift(1).fillna(False)
    arm_short = _armed(arm_short_raw, arm_window).shift(1).fillna(False)
    re_up = (
        B.crossed_above(df["fastK"], df["slowD"])
        | B.crossed_above(df["osc310"], df["osc310_sig"])
    ).fillna(False)
    re_dn = (
        B.crossed_below(df["fastK"], df["slowD"])
        | B.crossed_below(df["osc310"], df["osc310_sig"])
    ).fillna(False)
    df["long_entry"] = arm_long & df["uptrend"] & re_up
    df["short_entry"] = arm_short & df["downtrend"] & re_dn
    df["long_exit"] = (
        B.crossed_below(df["osc310"], df["osc310_sig"])
        | (df["downtrend"] & B.crossed_below(df["fastK"], df["slowD"]))
    ).fillna(False)
    df["short_exit"] = (
        B.crossed_above(df["osc310"], df["osc310_sig"])
        | (df["uptrend"] & B.crossed_above(df["fastK"], df["slowD"]))
    ).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
