"""Chaikin Money Flow + session VWAP signals.

Long when CMF(20) crosses above zero AND the close is above the
day's VWAP (money flow turning positive with price holding above
the session's volume-weighted average); short on the mirror.
Exit when CMF crosses back through zero OR the close crosses the
day VWAP against the position.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    above_vwap = df["c"] > df["vwap_day"]
    below_vwap = df["c"] < df["vwap_day"]
    df["long_entry"] = (
        crossed_above(df["cmf"], 0) & above_vwap
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        crossed_below(df["cmf"], 0) & below_vwap
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        crossed_below(df["cmf"], 0) | crossed_below(df["c"], df["vwap_day"])
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        crossed_above(df["cmf"], 0) | crossed_above(df["c"], df["vwap_day"])
    ).fillna(False).astype(bool)
    return df
