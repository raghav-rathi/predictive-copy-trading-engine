"""80-20 signals.

Over the 5 bars after a momentum bar: if price pushes >= 0.5xATR beyond
the momentum bar's close and then closes back INSIDE the momentum bar's
[low, high], enter the opposite direction (fade the momentum exhaustion).
Up-momentum fade -> short; down-momentum fade -> long.
Signal exits: none -- target / stop / max-hold from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mom_bar = df["mom_bar"].fillna(False)
    valid = df["mom_close"].notna() & (~mom_bar)  # s+1..s+5 after mom bar s
    # pushes are detected on every bar that has active momentum levels
    # (including chained momentum bars, which re-anchor the levels);
    # only the fade entry itself is barred from momentum bars.
    in_window = df["mom_close"].notna()
    pushed_up = ((df["h"] > df["mom_close"] + 0.5 * df["atr"]) & in_window)
    pushed_dn = ((df["l"] < df["mom_close"] - 0.5 * df["atr"]) & in_window)
    # push must have been seen on a valid bar up to and including this one
    pushed_up = ((pushed_up.rolling(6, min_periods=1).max() > 0) & valid).fillna(False)
    pushed_dn = ((pushed_dn.rolling(6, min_periods=1).max() > 0) & valid).fillna(False)
    back_inside = (df["c"] < df["mom_high"]) & (df["c"] > df["mom_low"])
    df["short_entry"] = (pushed_up & back_inside & (df["mom_up"] == 1.0)).fillna(False)
    df["long_entry"] = (pushed_dn & back_inside & (df["mom_up"] == 0.0)).fillna(False)
    df["long_exit"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
