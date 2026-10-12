"""Dual-Bear Pullback Short signals (short-only).

short_entry: on the first 1h bar of a new 4H block, when the daily
    regime gate holds (daily EMA21 < EMA55, developing daily close <
    EMA55, daily volume >= 20d SMA) AND the last two complete 4H bars
    are both bear bars AND the trigger bar pulled back to within
    0.5xATR(14) below 4H EMA21 AND trigger-bar 4H volume > its 20-bar
    SMA.
short_exit: 4H price reclaims 4H EMA21 (developing 4H close, i.e. the
    current 1h close, crosses above the developing 4H EMA21). This is
    the study's key finding — exits drive the edge. The harness also
    enforces the 2xATR hard stop and a 240-bar backstop (see risk.py).
Longs are never generated (short-only framework). Execution is
next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["short_entry"] = (
        df["new_block"] & df["regime_ok"] & df["h4_two_bear"]
        & df["pullback_ok"] & df["h4_vol_ok"]
    ).fillna(False).astype(bool)
    reclaim = (df["c"] > df["h4_ema21_dev"]) & df["h4_ema21_dev"].notna()
    df["short_exit"] = reclaim.fillna(False).astype(bool)
    df["long_entry"] = False
    df["long_exit"] = False
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
