"""Darvas Box signals (long-only).

Entry: the box top was CONFIRMED (3 bars failing to break it) on the prior
bar, the prior close sat at/below the prior box top, and the current close
breaks out above the box top with the volume filter. After a breakout the
rolling window naturally forms the new, higher box.

Exit: close below the box floor — the box is broken, Darvas' stop rule.

Deviation from the literal task spec: confirmation is evaluated on the
PRIOR bar (box_confirmed.shift(1)), not the signal bar. The breakout bar's
own high exceeds the box top by construction, so requiring
h[i] < box_top[i] on the signal bar would yield exactly zero trades. The
prior-bar evaluation preserves the intent — trade only confirmed boxes.

Long-only: short_entry / short_exit are always False.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_c = df["c"].shift(1)
    prev_top = df["box_top"].shift(1)
    prev_confirmed = df["box_confirmed"].shift(1).fillna(False)
    breakout = (prev_c <= prev_top) & (df["c"] > df["box_top"])
    df["long_entry"] = (breakout & prev_confirmed & df["vol_ok"]).fillna(False)
    df["long_exit"] = (df["c"] < df["box_bottom"]).fillna(False)
    df["short_entry"] = False
    df["short_exit"] = False
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
