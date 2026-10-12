"""LSMA slope signals: trend + momentum-alignment entries, slope-flip exits.

long_entry  = close > LSMA AND 5-bar LSMA slope > 0, freshly aligned
              (not aligned on the prior bar)
short_entry = close < LSMA AND 5-bar LSMA slope < 0, freshly aligned
long_exit   = LSMA slope flips negative
short_exit  = LSMA slope flips positive

Requiring both price-above-line and positive slope keeps entries out of
flat/ranging chop where price oscillates around the LSMA. Exits act on
the slope flip, which leads price -- the LSMA turns before the close
crosses it. Execution is next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = (df["c"] > df["lsma"]) & (df["lsma_slope"] > 0)
    dn = (df["c"] < df["lsma"]) & (df["lsma_slope"] < 0)
    aligned_up = up.fillna(False)
    aligned_dn = dn.fillna(False)
    df["long_entry"] = aligned_up & ~aligned_up.shift(1).fillna(False)
    df["short_entry"] = aligned_dn & ~aligned_dn.shift(1).fillna(False)
    df["long_exit"] = (df["lsma_slope"] < 0).fillna(False)
    df["short_exit"] = (df["lsma_slope"] > 0).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
