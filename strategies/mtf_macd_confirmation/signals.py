"""Multi-timeframe MACD confirmation signals (Elder Triple Screen).

Trade only in the direction of the higher-timeframe trend:

    Long entry:  1h MACD line crosses ABOVE its signal line
                 AND the 4h MACD histogram > 0.
    Short entry: 1h MACD line crosses BELOW its signal line
                 AND the 4h MACD histogram < 0.

    Long exit:   1h MACD line crosses back BELOW its signal
                 line OR the 4h MACD histogram crosses below 0
                 (or the opposite entry fires).
    Short exit:  mirror.

Entries are CROSS-based (crossed_above / crossed_below), never
level conditions, so a signal fires once per cross instead of
re-firing every bar the condition holds. Signal columns are
boolean, no NaN, no lookahead (execution at next-bar open is
handled by the harness). The house 2xATR hard stop / 3xATR
trail sit behind these exits, with a 168-bar max hold.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    macd = df["macd"]
    sig = df["macd_signal"]
    hist4 = df["macd_hist_4h"]

    cross_up = crossed_above(macd, sig)
    cross_down = crossed_below(macd, sig)
    hist4_cross_down = crossed_below(hist4, 0)
    hist4_cross_up = crossed_above(hist4, 0)

    long_entry = (cross_up & (hist4 > 0)).fillna(False).to_numpy(bool)
    short_entry = (cross_down & (hist4 < 0)).fillna(False).to_numpy(bool)
    # Opposite entry also exits (evaluated from the entry arrays
    # just built, so no ordering hazard).
    long_exit = (
        cross_down | hist4_cross_down | pd.Series(short_entry, index=df.index)
    ).fillna(False).to_numpy(bool)
    short_exit = (
        cross_up | hist4_cross_up | pd.Series(long_entry, index=df.index)
    ).fillna(False).to_numpy(bool)

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
