"""Woodies CCI "Zero-Line Reject" signals (mechanical version).

Ken Wood's pattern family keys off the trend CCI's relationship to
the zero line; this engine implements the Zero-Line Reject — the
most mechanical of the family, no chart reading required.

Trend filter: cci14 must sit on one side of the zero line for
TREND_BARS consecutive bars. Six bars of +CCI says bulls own the
trend; six bars of -CCI says bears do.

Long setup: trend is bullish (6+ bars above zero) AND cci14 has
pulled back into [0, 50] — the "reject" zone where the trend line
tags toward the zero line without crossing it.

Long entry: the fast turbo CCI(6) hooks back up through zero while
the pullback setup is in force — the trigger re-aligns with the
trend.

Short mirror: 6+ bars below zero, cci14 in [-50, 0], turbo crosses
below zero.

Exits: the trend line itself crossing the zero line — long exits on
cci14 crossing below 0, short exits on cci14 crossing above 0. Once
the trend line loses its side of the zero line, the premise is
gone; the harness's trail/stop handles the rest.

``trend_bars`` is a parameter (shipped default 6) so sensitivity can
be swept honestly. Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

TREND_BARS = 6  # shipped default
PULLBACK_TOP = 50.0


def _level(df: pd.DataFrame, value: float) -> pd.Series:
    return pd.Series(float(value), index=df.index)


def add_signals(df: pd.DataFrame, trend_bars: int = TREND_BARS) -> pd.DataFrame:
    df = df.copy()
    trend = df["cci14"]
    turbo = df["turbo"]
    zero = _level(df, 0.0)

    above = (trend > 0).rolling(trend_bars, min_periods=trend_bars).sum() >= trend_bars
    below = (trend < 0).rolling(trend_bars, min_periods=trend_bars).sum() >= trend_bars
    long_trend = above.fillna(False)
    short_trend = below.fillna(False)

    long_pullback = long_trend & (trend >= 0) & (trend <= PULLBACK_TOP)
    short_pullback = short_trend & (trend <= 0) & (trend >= -PULLBACK_TOP)

    long_entry = (long_pullback & crossed_above(turbo, zero)).fillna(False)
    short_entry = (short_pullback & crossed_below(turbo, zero)).fillna(False)
    long_exit = crossed_below(trend, zero).fillna(False)
    short_exit = crossed_above(trend, zero).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
