"""Hurst exponent regime signals.

Trend mode (mode == +1): EMA(20/50) cross entries in the trend
direction — long on a cross up, short on a cross down. Exit on
the opposite cross or a close through the EMA(50) invalidation.
Reversion mode (mode == -1): RSI(14) extremes — long on RSI
crossing below 30, short on RSI crossing above 70. Exit on RSI
crossing back through 50. Neutral mode (mode == 0): no entries;
no signal exits either (the position is carried by the harness
stop / trail / max hold until the mode re-engages).

Exits are mode-gated on the mode in force on the signal bar, so
a trade opened in one mode is exited by that mode's rules while
the mode persists; if the mode flips mid-trade, the new mode's
exit rules take over.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mode = df["mode"].fillna(0).astype(int)
    trend = mode == 1
    revert = mode == -1

    ema20 = df["ema20"]
    ema50 = df["ema50"]
    rsi = df["rsi14"]
    c = df["c"]

    cross_up = B.crossed_above(ema20, ema50).fillna(False)
    cross_down = B.crossed_below(ema20, ema50).fillna(False)
    rsi_below_30 = B.crossed_below(rsi, 30).fillna(False)
    rsi_above_70 = B.crossed_above(rsi, 70).fillna(False)
    rsi_up_50 = B.crossed_above(rsi, 50).fillna(False)
    rsi_down_50 = B.crossed_below(rsi, 50).fillna(False)

    df["long_entry"] = ((trend & cross_up) | (revert & rsi_below_30)).fillna(False).astype(bool)
    df["short_entry"] = ((trend & cross_down) | (revert & rsi_above_70)).fillna(False).astype(bool)
    df["long_exit"] = (
        (trend & (cross_down | (c < ema50))) | (revert & rsi_up_50)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        (trend & (cross_up | (c > ema50))) | (revert & rsi_down_50)
    ).fillna(False).astype(bool)
    return df
