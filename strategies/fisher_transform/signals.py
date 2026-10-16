"""Ehlers Fisher Transform reversal signals.

Two variants calibrated head-to-head (see BACKTEST.md):
  plain -- cross fisher/trigger entries, no regime filter
  gated -- same entries, additionally requiring ADX(14) > 20
Exits (both variants): cross-back OR extreme level (fisher > 2.5 / < -2.5).

add_signals delegates to the calibration winner.
"""

import pandas as pd

from strategies import base as B

OVERBOUGHT = 2.5
OVERSOLD = -2.5
ADX_MIN = 20.0


def _exits(df: pd.DataFrame) -> pd.DataFrame:
    df["long_exit"] = B.crossed_below(df["fisher"], df["fisher_trigger"]) | (df["fisher"] > OVERBOUGHT)
    df["short_exit"] = B.crossed_above(df["fisher"], df["fisher_trigger"]) | (df["fisher"] < OVERSOLD)
    return df


def add_signals_plain(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = B.crossed_above(df["fisher"], df["fisher_trigger"])
    df["short_entry"] = B.crossed_below(df["fisher"], df["fisher_trigger"])
    _exits(df)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df


def add_signals_gated(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    regime = df["adx14"] > ADX_MIN
    df["long_entry"] = B.crossed_above(df["fisher"], df["fisher_trigger"]) & regime
    df["short_entry"] = B.crossed_below(df["fisher"], df["fisher_trigger"]) & regime
    _exits(df)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df


# Calibration 2026-10-09 on BTC/ETH/HYPE 1h (365d, costs on): gated won on
# combined net PnL (-$19,703 vs -$24,511 plain). Both variants lost money —
# honest verdict in BACKTEST.md.
add_signals = add_signals_gated
