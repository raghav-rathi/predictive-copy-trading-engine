"""Ichimoku Tenkan-sen / Kijun-sen cross signals.

Long: Tenkan-sen crosses above Kijun-sen. Short: Tenkan-sen crosses
below Kijun-sen. Exit on the opposite cross. No cloud, price, or
Chikou filter — the cross alone, exactly as briefed.

DISTINCTION from the existing strategies/kijun_cross: that strategy
trades the CLOSE crossing the Kijun-sen (price vs baseline). This
strategy trades the two Ichimoku lines crossing EACH OTHER
(Tenkan-sen vs Kijun-sen). Different trigger, different trades.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["tenkan"], df["kijun"]).fillna(False)
    cross_down = crossed_below(df["tenkan"], df["kijun"]).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_down.astype(bool)
    df["long_exit"] = cross_down.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
