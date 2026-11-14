"""Dynamic Zones RSI signals.

    long_entry  = RSI crosses back above buy_zone (oversold bounce)
    short_entry = RSI crosses back below sell_zone (overbought fade)
    long_exit   = RSI crosses below 50, or touches the sell zone
    short_exit  = RSI crosses above 50, or touches the buy zone

A cross back above the buy zone implies the prior bar was at/below
the zone (crossed_above requires prev <= zone), so the "after dipping
below it" condition is built into the cross itself -- no extra state
needed. Exits are cross-driven, not exit-on-first-weakness: RSI
crossing 50 means momentum has returned to neutral, and touching the
opposite zone means the move has reached the other extreme.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = df["rsi"]
    buy = df["buy_zone"]
    sell = df["sell_zone"]
    cross_up_buy = crossed_above(rsi, buy).fillna(False)
    cross_dn_sell = crossed_below(rsi, sell).fillna(False)
    cross_dn_50 = crossed_below(rsi, 50).fillna(False)
    cross_up_50 = crossed_above(rsi, 50).fillna(False)
    cross_up_sell = crossed_above(rsi, sell).fillna(False)
    cross_dn_buy = crossed_below(rsi, buy).fillna(False)
    df["long_entry"] = cross_up_buy.astype(bool)
    df["short_entry"] = cross_dn_sell.astype(bool)
    df["long_exit"] = (cross_dn_50 | cross_up_sell).astype(bool)
    df["short_exit"] = (cross_up_50 | cross_dn_buy).astype(bool)
    return df
