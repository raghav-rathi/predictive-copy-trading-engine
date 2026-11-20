"""VWAP Bollinger Bands signals (mean reversion in a ranging regime).

Long entry:  close below the lower band AND ADX(14) < 25.
Short entry: close above the upper band AND ADX(14) < 25.
Long exit:   close back at/through VWAP.
Short exit:  close back at/through VWAP.

The ADX < 25 filter is the ranging-regime gate: band fades are only
taken when there is no strong trend. The harness risk layer's
2xATR stop / 2.5xATR trail also applies. Signal columns are boolean,
no NaN, no lookahead (the harness executes at the next bar's open).
"""

import pandas as pd

ADX_MAX = 25


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ranging = (df["adx"] < ADX_MAX).fillna(False)
    df["long_entry"] = ((df["c"] < df["vwap_lower"]) & ranging).fillna(False).astype(bool)
    df["short_entry"] = ((df["c"] > df["vwap_upper"]) & ranging).fillna(False).astype(bool)
    df["long_exit"] = (df["c"] >= df["vwap"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] <= df["vwap"]).fillna(False).astype(bool)
    return df
