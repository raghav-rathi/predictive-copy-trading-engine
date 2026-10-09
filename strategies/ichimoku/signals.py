"""Ichimoku signals (classic, no-lookahead).

Long  when: close above cloud AND Tenkan crosses above Kijun
            AND Chikou confirmation: close > high of 26 bars ago
            (the Chikou line plots today's close 26 bars back; it must
            clear the price action sitting there — no future data used)
Short when: close below cloud AND Tenkan crosses below Kijun
            AND close < low of 26 bars ago
Exit long  on Tenkan cross below Kijun, or close below Kijun.
Exit short on Tenkan cross above Kijun, or close above Kijun.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.ichimoku.indicators import KIJUN


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = (
        df["senkou_a"].notna()
        & df["tenkan"].notna()
        & df["h"].shift(KIJUN).notna()
    )
    above_cloud = df["c"] > df["cloud_top"]
    below_cloud = df["c"] < df["cloud_bot"]
    tk_up = crossed_above(df["tenkan"], df["kijun"])
    tk_dn = crossed_below(df["tenkan"], df["kijun"])
    chikou_ok_long = df["c"] > df["h"].shift(KIJUN)
    chikou_ok_short = df["c"] < df["l"].shift(KIJUN)
    df["long_entry"] = above_cloud & tk_up & chikou_ok_long & valid
    df["short_entry"] = below_cloud & tk_dn & chikou_ok_short & valid
    df["long_exit"] = tk_dn | (df["c"] < df["kijun"])
    df["short_exit"] = tk_up | (df["c"] > df["kijun"])
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
