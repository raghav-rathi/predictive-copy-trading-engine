"""Point & Figure signals — the classic double-top / double-bottom
breakout of the 3-box reversal method.

  long_entry:  active X column's top crosses >= 1 box above the previous
               X column's top (double-top break)
  short_entry: active O column's bottom crosses >= 1 box below the
               previous O column's bottom (double-bottom break)
  long_exit / short_exit: the opposite breakout (trend turn on the chart)

The P&F state at bar i uses only closes through bar i, so the signal is
lookahead-free; the harness executes it at bar i+1's open.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    box = df["pf_box"]
    is_x = df["pf_col"] == 1
    is_o = df["pf_col"] == -1

    dt_ratio = (df["pf_top"] - df["pf_prev_x_top"]) / box
    db_ratio = (df["pf_prev_o_bottom"] - df["pf_bottom"]) / box

    dt = is_x & (dt_ratio >= 1.0)
    db = is_o & (db_ratio >= 1.0)

    df["long_entry"] = (dt & ~dt.shift(1).fillna(False)).fillna(False)
    df["short_entry"] = (db & ~db.shift(1).fillna(False)).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
