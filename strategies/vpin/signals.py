"""VPIN toxicity-exhaustion signals.

Experimental exhaustion read of the academic VPIN toxicity metric:
extreme order-flow toxicity (VPIN percentile > 0.90) combined with a
panic extreme of price (new 20-bar low / high) is traded as a
mean-reversion fade — the informed flow has been absorbed and the move
is exhausted.

Long:  vpin_pctile > 0.90 AND close makes a new 20-bar low.
Short: vpin_pctile > 0.90 AND close makes a new 20-bar high.
Exits: none from the signal side — the risk config manages the trade
(2xATR stop, 2xATR target, 48-bar max hold).
"""

from __future__ import annotations

import pandas as pd

PCTILE_TRIGGER = 0.90


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    toxic = (df["vpin_pctile"] > PCTILE_TRIGGER).fillna(False)
    panic_low = (df["c"] <= df["low_20"]).fillna(False)
    panic_high = (df["c"] >= df["high_20"]).fillna(False)
    out["long_entry"] = (toxic & panic_low).astype(bool)
    out["short_entry"] = (toxic & ~panic_low & panic_high).astype(bool)
    out["long_exit"] = pd.Series(False, index=df.index)
    out["short_exit"] = pd.Series(False, index=df.index)
    return out
