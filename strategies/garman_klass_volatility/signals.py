"""Garman-Klass volatility-expansion signals.

Long: realized volatility (gk_vol) crosses ABOVE its slow
baseline (gk_vol_sma) -- a volatility expansion -- while the
close sits above EMA(20) (trend up). Short: the same vol
cross while the close sits below EMA(20) (trend down). Both
sides cannot fire on one bar: the close cannot be both above
and below EMA(20), so the guard is defensive only.

Exit: volatility crosses back BELOW its baseline, or the
close crosses the wrong side of EMA(20) (trend lost). The
house 2xATR hard stop / 3xATR trail sit behind these exits,
with a 72-bar max hold.

Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
Entries are CROSS-based (crossed_above on gk_vol vs
gk_vol_sma), never level conditions: a level condition
would re-fire every bar volatility sat above its baseline.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vol_up = crossed_above(df["gk_vol"], df["gk_vol_sma"]).fillna(False)
    vol_dn = crossed_below(df["gk_vol"], df["gk_vol_sma"]).fillna(False)
    above_ema = (df["c"] > df["ema20"]).fillna(False)
    below_ema = (df["c"] < df["ema20"]).fillna(False)
    long_entry = (vol_up & above_ema).astype(bool)
    short_entry = (vol_up & below_ema).astype(bool)
    # Defensive guard: both triggers on one bar -> neither.
    both = long_entry & short_entry
    long_entry = long_entry & ~both
    short_entry = short_entry & ~both
    long_exit = (
        vol_dn | crossed_below(df["c"], df["ema20"]).fillna(False)
    ).astype(bool)
    short_exit = (
        vol_dn | crossed_above(df["c"], df["ema20"]).fillna(False)
    ).astype(bool)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
