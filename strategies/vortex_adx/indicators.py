"""Vortex indicator + ADX filter (Etienne Botes & Douglas Siepman,
Technical Analysis of Stocks & Commodities, January 2010).

Per bar:

    VM+ = |high - previous low|
    VM- = |low - previous high|
    TR  = Wilder true range

    VI+ = EMA(VM+, 14) / EMA(TR, 14)
    VI- = EMA(VM-, 14) / EMA(TR, 14)

ADX(14) is the shared strategies.base.adx primitive (Wilder smoothing).
The ADX(14) > 25 entry filter and ADX(14) < 20 exit use the same
14-bar length as the Vortex lines.

Note on the smoothing: Botes & Siepman publish VI as a 14-period SUM
ratio (sum of VM over 14 bars / sum of TR over 14 bars). This build
uses EMA(14) ratios instead, per the batch spec (see CALIBRATION.md);
the cross logic is unchanged, but the lines are exponentially
weighted rather than equally weighted.

Columns: vi_plus, vi_minus, adx, atr.

No lookahead: every value on bar i uses data through bar i's close
(EMA min_periods -> leading NaN warmup).
"""

import pandas as pd

from strategies import base as B

N = 14

INDICATOR_COLS = ["vi_plus", "vi_minus", "adx", "atr"]


def add_indicators(df: pd.DataFrame, n: int = N) -> pd.DataFrame:
    df = df.copy()
    vm_plus = (df["h"] - df["l"].shift(1)).abs()
    vm_minus = (df["l"] - df["h"].shift(1)).abs()
    tr = B.true_range(df["h"], df["l"], df["c"])
    df["vi_plus"] = B.ema(vm_plus, n) / B.ema(tr, n)
    df["vi_minus"] = B.ema(vm_minus, n) / B.ema(tr, n)
    df["adx"] = B.adx(df["h"], df["l"], df["c"], n)["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
