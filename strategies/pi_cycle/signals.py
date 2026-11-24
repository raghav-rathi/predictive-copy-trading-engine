"""Pi Cycle Top regime signals (Philip Swift, 2019).

Long regime while sma111 < MULT * sma350; short regime (the "top
zone") while sma111 >= MULT * sma350.

    long_entry  -- sma111 crosses back BELOW pi_top (exiting the top zone)
    short_entry -- sma111 crosses ABOVE pi_top (the top signal)
    long_exit   -- sma111 crosses above pi_top (opposite cross)
    short_exit  -- sma111 crosses below pi_top (opposite cross)

Crossings are computed with crossed_above/crossed_below on the
indicator columns, so the signal on bar j uses data through bar
j's close only; execution at the next bar's open is the harness's
job. The pi_top column is read from the indicator frame when
present, so a calibration sweep can vary the multiplier through
add_indicators alone; the ``mult`` parameter is only used when the
frame lacks a pi_top column.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

MULT = 2.0  # shipped default; must match indicators.MULT


def add_signals(df: pd.DataFrame, mult: float = MULT) -> pd.DataFrame:
    df = df.copy()
    fast = df["sma111"]
    if "pi_top" in df.columns:
        top = df["pi_top"]
    else:
        top = mult * df["sma350"]
    long_entry = crossed_below(fast, top).fillna(False)
    short_entry = crossed_above(fast, top).fillna(False)
    long_exit = crossed_above(fast, top).fillna(False)
    short_exit = crossed_below(fast, top).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
