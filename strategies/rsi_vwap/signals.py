"""RSI(14) + session VWAP signals.

Long: RSI(14) crosses up through 30 while the close is above
the session VWAP (oversold bounce with price already above
the day's value area).
Short: RSI(14) crosses down through 70 while the close is
below the session VWAP.
Exit: RSI crosses 50 against the position (long exits on RSI
crossing below 50; short on RSI crossing above 50) OR the
close crosses the session VWAP against the position (long
exits on a close below VWAP; short on a close above VWAP).
The house 2xATR hard stop / 3xATR trail and 120-bar max hold
sit behind these exits.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness). The VWAP side
uses the current bar's close vs the current bar's VWAP --
both are known at the close, so there is no lookahead; the
RSI crosses use crossed_above / crossed_below, which compare
against the prior bar's values.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

RSI_OVERSOLD = 30.0
RSI_OVERBOUGHT = 70.0
RSI_MID = 50.0


def add_signals(
    df: pd.DataFrame,
    rsi_oversold: float = RSI_OVERSOLD,
    rsi_overbought: float = RSI_OVERBOUGHT,
    rsi_mid: float = RSI_MID,
) -> pd.DataFrame:
    df = df.copy()
    rsi = df["rsi"]
    vwap = df["vwap"]
    df["long_entry"] = (
        crossed_above(rsi, rsi_oversold) & (df["c"] > vwap)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        crossed_below(rsi, rsi_overbought) & (df["c"] < vwap)
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        crossed_below(rsi, rsi_mid) | crossed_below(df["c"], vwap)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        crossed_above(rsi, rsi_mid) | crossed_above(df["c"], vwap)
    ).fillna(False).astype(bool)
    return df
