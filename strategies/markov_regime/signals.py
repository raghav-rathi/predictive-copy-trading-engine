"""Markov regime-switching signals (Hamilton, 1989).

The HMM regime (see indicators.py) selects which system trades:

    Calm state (regime 0):     EMA(12)/EMA(26) cross (trend).
        Long entry:  EMA fast crosses above EMA slow.
        Short entry: EMA fast crosses below EMA slow.
    Turbulent state (regime 1): RSI(14) mean reversion.
        Long entry:  RSI crosses up through 30.
        Short entry: RSI crosses down through 70.
        Mean-reversion exit at RSI 50.

Entries:

    long_entry  = (calm & EMA cross up) | (turbulent & RSI cross up 30)
    short_entry = (calm & EMA cross down) | (turbulent & RSI cross down 70)

Exits fire on either system's exit, whatever the current regime
(the position is closed by the first exit that triggers):

    long_exit  = EMA cross down | RSI cross down through 50
    short_exit = EMA cross up | RSI cross up through 50

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). The harness risk layer's
2xATR stop / 2.5xATR trail / 120-bar max hold also applies.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    calm = (df["regime"] == 0).fillna(True)
    turbulent = (df["regime"] == 1).fillna(False)
    ema_up = B.crossed_above(df["ema_fast"], df["ema_slow"])
    ema_dn = B.crossed_below(df["ema_fast"], df["ema_slow"])
    rsi_up30 = B.crossed_above(df["rsi"], 30.0)
    rsi_dn70 = B.crossed_below(df["rsi"], 70.0)
    rsi_dn50 = B.crossed_below(df["rsi"], 50.0)
    rsi_up50 = B.crossed_above(df["rsi"], 50.0)
    long_entry = ((calm & ema_up) | (turbulent & rsi_up30))
    short_entry = ((calm & ema_dn) | (turbulent & rsi_dn70))
    long_exit = (ema_dn | rsi_dn50)
    short_exit = (ema_up | rsi_up50)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
