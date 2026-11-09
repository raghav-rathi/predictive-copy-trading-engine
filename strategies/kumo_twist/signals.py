"""Ichimoku Kumo twist signals.

Long: Senkou Span A crosses above Senkou Span B (cloud twists bullish).
Short: Senkou Span A crosses below Senkou Span B (cloud twists bearish).
Exit on the opposite twist. The spans are the causal, unshifted values
computed from data through bar i (see indicators.py) — the twist is
detected when the current cloud changes colour, not 26 bars ahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    twist_up = crossed_above(df["senkou_a"], df["senkou_b"]).fillna(False)
    twist_down = crossed_below(df["senkou_a"], df["senkou_b"]).fillna(False)
    df["long_entry"] = twist_up.astype(bool)
    df["short_entry"] = twist_down.astype(bool)
    df["long_exit"] = twist_down.astype(bool)
    df["short_exit"] = twist_up.astype(bool)
    return df
