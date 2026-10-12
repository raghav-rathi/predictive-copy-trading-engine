"""Asia Sweep signals.

Long:  inside a signal window (07/08/09 or 12/13 UTC), the signal bar's
    low sweeps the prior session's low (low <= ref_low) but closes back
    above it (close > ref_low) as a bullish candle (close > open), bias
    is bullish (+1), and sweep depth (ref_low - low) >= DEPTH_ATR_MULT *
    ATR(14).
Short: mirror image on ref_high with bearish bias and bearish candle.
Reversing exits: opposite-side sweep closes the position
(long_exit == short_entry, short_exit == long_entry). Additionally the
book is flattened at the 20:00 UTC bar (spec: kill at 20:00 UTC close);
the harness executes that exit at the 21:00 open. Stops/targets live in
risk.py (spec: SL = sweep extreme -/+ 0.5xATR, TP = 3R; the harness
anchors stops at entry, so the shipped 1.0xATR stop is a calibrated
approximation — see BACKTEST.md). Execution is next-bar-open per the
harness contract.
"""

import pandas as pd

DEPTH_ATR_MULT = 0.10  # sweep must reach >= 0.10 x ATR beyond the extreme


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    in_window = df["hour"].isin([7, 8, 9, 12, 13])
    ref_ok = df["ref_low"].notna() & df["ref_high"].notna() & df["atr"].notna()
    bull_bias = df["bias"] == 1.0
    bear_bias = df["bias"] == -1.0

    long_sweep = (
        in_window & ref_ok & bull_bias
        & (df["l"] <= df["ref_low"])            # swept the prior low
        & (df["c"] > df["ref_low"])             # closed back above
        & (df["c"] > df["o"])                   # bullish candle
        & ((df["ref_low"] - df["l"]) >= DEPTH_ATR_MULT * df["atr"])
    )
    short_sweep = (
        in_window & ref_ok & bear_bias
        & (df["h"] >= df["ref_high"])           # swept the prior high
        & (df["c"] < df["ref_high"])           # closed back below
        & (df["c"] < df["o"])                   # bearish candle
        & ((df["h"] - df["ref_high"]) >= DEPTH_ATR_MULT * df["atr"])
    )
    df["long_entry"] = long_sweep
    df["short_entry"] = short_sweep
    kill = df["kill_20"].fillna(False).astype(bool)
    # reversing exits + 20:00 UTC flat
    df["long_exit"] = df["short_entry"] | kill
    df["short_exit"] = df["long_entry"] | kill
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
