"""Anchored VWAP reversion indicators.

Institutional VWAP (anchored to each UTC day): distance from VWAP measured
in ATR units (z-score). Stretched moves revert to VWAP intraday — the
bread-and-butter of intraday equity/futures desks, ported to crypto perps.
"""

import pandas as pd

from strategies import base as B

Z_ENTRY = 1.5  # enter when |z| > 1.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["vwap"] = B.anchored_vwap(df["h"], df["l"], df["c"], df["v"], df["t"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    df["vwap_z"] = (df["c"] - df["vwap"]) / df["atr"]
    return df
