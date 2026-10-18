"""ICT Silver Bullet killzone signals (Michael Huddleston).

Long: inside a NY killzone + bullish 4h-EMA bias + price touches an
unmitigated bullish FVG printed earlier the same NY day + market-
structure shift (close above the last 3-bar micro swing high).
Short mirrors it. The opposite setup's entry reverses the position;
the 0.75xATR stop (FVG-extreme proxy), 1.5xATR target (2R) and 24-bar
max hold (session end) come from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kz = df["in_killzone"].fillna(False)
    df["long_entry"] = (
        kz & df["bias_bull"] & df["bull_fvg_touch"] & df["mss_bull"]
    ).fillna(False)
    df["short_entry"] = (
        kz & df["bias_bear"] & df["bear_fvg_touch"] & df["mss_bear"]
    ).fillna(False)
    # the opposite killzone setup reverses the position
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
