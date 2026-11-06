"""Rounding Bottom signals.

Long: close above the (prior-bar) rounding-bottom neckline with volume
above its 20-bar average, within 20 bars of the pattern detection.
Exit long: close back below the neckline (within 120 bars of detection).
Short side is the rounding-top mirror: close below the neckline with
volume confirmation; exit short on a close back above it.

Neckline, pattern age and volume average are all shifted by 1, so the
close is never compared with a neckline computed from the current bar.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    neck_b = df["neckline_bottom"].shift(1)
    neck_t = df["neckline_top"].shift(1)
    age_b = df["rb_bars_since"].shift(1)
    age_t = df["rt_bars_since"].shift(1)
    vol_ok = df["v"] > df["vol_sma20"].shift(1)

    df["long_entry"] = (
        (df["c"] > neck_b) & vol_ok & (age_b <= 20)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (df["c"] < neck_t) & vol_ok & (age_t <= 20)
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        (df["c"] < neck_b) & (age_b <= 120)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        (df["c"] > neck_t) & (age_t <= 120)
    ).fillna(False).astype(bool)
    return df
