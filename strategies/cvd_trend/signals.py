"""CVD trend signals.

    rising2 = cvd_slope > 0 on this bar AND the previous bar
              (EMA(CVD,20) rising for 2 consecutive bars)
    falling2 = cvd_slope < 0 on this bar AND the previous bar

    long_entry  = rising2 turns on (first bar of a 2-bar rise)
                  with close above EMA(50)
    short_entry = falling2 turns on (first bar of a 2-bar fall)
                  with close below EMA(50)
    long_exit   = cvd_slope reverses (turns negative)
    short_exit  = cvd_slope reverses (turns positive)

Entries fire once per slope streak (the "turns on" condition), not on
every rising bar — the backtest only enters when flat, but the
once-per-streak form keeps the signal count honest. Exits are the
slope reversal itself: a long is out the moment order flow stops
buying, even if price has not yet turned.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    s = df["cvd_slope"]
    rising2 = ((s > 0) & (s.shift(1) > 0)).fillna(False)
    falling2 = ((s < 0) & (s.shift(1) < 0)).fillna(False)
    rise_on = (rising2 & (~rising2.shift(1).fillna(False))).fillna(False)
    fall_on = (falling2 & (~falling2.shift(1).fillna(False))).fillna(False)
    df["long_entry"] = (rise_on & (df["c"] > df["ema50"])).astype(bool)
    df["short_entry"] = (fall_on & (df["c"] < df["ema50"])).astype(bool)
    df["long_exit"] = (s < 0).fillna(False).astype(bool)
    df["short_exit"] = (s > 0).fillna(False).astype(bool)
    return df
