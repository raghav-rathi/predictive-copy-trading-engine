"""Darvas Box indicators (Nicolas Darvas, Box Theory — long-only port).

Box top = max high over the trailing ``box_n + 1``-bar window, excluding the
last CONFIRM_BARS bars:
    box_top[i] = max(h) over bars [i - box_n - 3, i - 3].
The top is CONFIRMED at bar i when the 3 most recent highs all failed to
break it (h[i], h[i-1], h[i-2] < box_top[i]) — Darvas' rule for a valid box
ceiling.

Box bottom = min low over [top_bar, i - 1], where top_bar is the bar where
the rolling window max was set — the box floor (Darvas' stop level).

Volume filter: vol_sma20 = SMA(v, 20); a breakout bar needs
v[i] > vol_mult * vol_sma20[i] (Darvas demanded expanding volume on the
breakout bar).

No lookahead: every rolling value uses only bars through the current close.
The optional ``box_n`` / ``vol_mult`` parameters are for calibration sweeps;
the registered strategy always uses the shipped defaults.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BOX_N = 60
CONFIRM_BARS = 3
VOL_N = 20
VOL_MULT = 1.25


def add_indicators(
    df: pd.DataFrame, box_n: int = BOX_N, vol_mult: float = VOL_MULT
) -> pd.DataFrame:
    df = df.copy()
    w = box_n + 1
    # trailing window excluding the last CONFIRM_BARS bars
    raw_top = df["h"].rolling(w, min_periods=w).max()
    # 0-based position of the max inside each window -> bar where the top set
    raw_pos = df["h"].rolling(w, min_periods=w).apply(
        lambda a: float(np.argmax(a)), raw=True
    )
    idx = pd.Series(np.arange(len(df)), index=df.index)
    top_bar = (idx - (w - 1 - raw_pos)).shift(CONFIRM_BARS)
    box_top = raw_top.shift(CONFIRM_BARS)
    df["box_top"] = box_top
    df["box_top_bar"] = top_bar
    h0, h1, h2 = df["h"], df["h"].shift(1), df["h"].shift(2)
    df["box_confirmed"] = ((h0 < box_top) & (h1 < box_top) & (h2 < box_top)).fillna(False)
    # box floor: min low from the bar where the top was set through bar i-1
    lows = df["l"].to_numpy(dtype=float)
    tb = top_bar.to_numpy(dtype=float)
    top_ok = (~box_top.isna()).to_numpy()
    bottom = np.full(len(df), np.nan)
    for i in range(len(df)):
        if not top_ok[i] or np.isnan(tb[i]):
            continue
        a = int(tb[i])
        if 0 <= a < i:
            bottom[i] = lows[a:i].min()
    df["box_bottom"] = bottom
    df["vol_sma20"] = B.sma(df["v"], VOL_N)
    df["vol_ok"] = (df["v"] > vol_mult * df["vol_sma20"]).fillna(False)
    return df
