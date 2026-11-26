"""Connors TPS signals.

Long: close > SMA(200) (uptrend) AND RSI(2) below 25 for two
consecutive bars — the entry fires on the close of the second
bar, executed at next-bar open by the harness. Short is the
mirror: close < SMA(200) AND RSI(2) above 75 for two
consecutive bars.
Exit: RSI(2) closes above 70 (long) / below 30 (short), OR
the 10-bar time exit — the book's day-11 exit, scaled to 1h
and enforced by the harness max_hold_bars=10 in risk.py.
Level conditions are used for the exits: the harness checks
them every bar while a position is open, so the first bar
above 70 (below 30) exits, exactly as a cross would.

The original system has no stop — the house 2xATR stop /
3xATR trail is added as a deviation required by house risk
rules (see README.md). No lookahead: every condition reads
bar i and bar i-1 only. Signal columns are boolean, no NaN.
"""

import pandas as pd

ENTRY_LOW = 25.0
ENTRY_HIGH = 75.0
EXIT_HIGH = 70.0
EXIT_LOW = 30.0
SMA_N = 200


def add_signals(
    df: pd.DataFrame,
    entry_low: float = ENTRY_LOW,
    entry_high: float = ENTRY_HIGH,
    exit_high: float = EXIT_HIGH,
    exit_low: float = EXIT_LOW,
    sma_n: int = SMA_N,
) -> pd.DataFrame:
    df = df.copy()
    rsi2 = df["rsi2"]
    sma = df[f"sma{sma_n}"]
    rsi2_prev = rsi2.shift(1)
    long_setup = (rsi2 < entry_low) & (rsi2_prev < entry_low)
    short_setup = (rsi2 > entry_high) & (rsi2_prev > entry_high)
    df["long_entry"] = (
        (df["c"] > sma) & long_setup
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (df["c"] < sma) & short_setup
    ).fillna(False).astype(bool)
    df["long_exit"] = (rsi2 > exit_high).fillna(False).astype(bool)
    df["short_exit"] = (rsi2 < exit_low).fillna(False).astype(bool)
    return df
