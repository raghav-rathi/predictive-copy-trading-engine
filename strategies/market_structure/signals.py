"""Market-structure signals.

long_entry  = bullish BOS while direction is already +1 (continuation)
              OR bullish CHoCH (reversal into a new up-leg)
short_entry = bearish BOS while direction is already -1
              OR bearish CHoCH
long_exit   = bearish BOS (structure breaks against the long)
short_exit  = bullish BOS
Execution next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bu, bd = df["bos_up"], df["bos_dn"]
    cu, cd = df["choch_up"], df["choch_dn"]
    d = df["ms_direction"]
    df["long_entry"] = ((bu & (d == 1.0)) | cu).fillna(False)
    df["short_entry"] = ((bd & (d == -1.0)) | cd).fillna(False)
    df["long_exit"] = bd.fillna(False)
    df["short_exit"] = bu.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
