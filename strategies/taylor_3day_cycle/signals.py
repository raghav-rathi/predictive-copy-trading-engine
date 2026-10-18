"""Taylor 3-day cycle signals.

  Buy Day:      long on a dip to within 0.1xATR of the prior day's low
                that recovers (close > open); exit at a touch of the
                prior day's high.
  Sell Day:     no new entries (rally/exit day for Buy-Day longs).
  Sell-Short Day: short on a rally to within 0.1xATR of the prior day's
                high that rejects (close < open); exit at a touch of the
                prior day's low.
Residual exits (1xATR stop, 24-bar max hold ~ one day) come from risk.py.
"""

import pandas as pd

from strategies.taylor_3day_cycle import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    label = df["cycle_label"]
    df["long_entry"] = (
        (label == I.BUY_DAY) & df["long_cand"]
    ).fillna(False)
    df["short_entry"] = (
        (label == I.SELL_SHORT_DAY) & df["short_cand"]
    ).fillna(False)
    df["long_exit"] = (df["h"] >= df["prior_day_high"]).fillna(False)
    df["short_exit"] = (df["l"] <= df["prior_day_low"]).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
