"""RSI vs its SMA signal-line cross, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(rsi, rsi_sma)
    short_entry = crossed_below(rsi, rsi_sma)

This is a momentum-cross trade, not an overbought/oversold fade:
RSI crossing above its own 14-bar average means upside momentum
is accelerating relative to its recent norm; crossing below
means downside momentum is accelerating. No level filter (no
30/70 gate) — the cross itself is the whole thesis, so adding a
level gate would turn it into a different strategy. In chop the
RSI whipsaws across its average, which is the known cost of the
setup; the ATR stop/trail and 72-bar max hold are the only
defences, by design.

Exits are the pure opposite crosses:

    long_exit  = crossed_below(rsi, rsi_sma)
    short_exit = crossed_above(rsi, rsi_sma)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = df["rsi"]
    rsi_sma = df["rsi_sma"]

    xup = crossed_above(rsi, rsi_sma).fillna(False)
    xdn = crossed_below(rsi, rsi_sma).fillna(False)

    df["long_entry"] = xup.astype(bool)
    df["short_entry"] = xdn.astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
