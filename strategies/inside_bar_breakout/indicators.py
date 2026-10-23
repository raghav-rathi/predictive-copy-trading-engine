"""Inside bar / mother bar breakout -- contraction-then-expansion price action.

An inside bar is strict: its WHOLE range sits inside the prior
(mother) bar's range::

    inside = (h < h.shift(1)) & (l > l.shift(1))

The contraction (inside bar) marks volatility compression; the
trade is the expansion: a close beyond the mother bar's extreme.
On an inside bar the setup arms with mother_high = prior-bar high
and mother_low = prior-bar low; the levels stay armed for up to
5 bars (setup expiry window) -- after 5 bars with no breakout the
setup expires. A newer inside bar inside the window resets the
levels (fresh setup).

Columns:

    inside               -- strict inside bar flag
    mother_high          -- prior-bar h on inside bars, else NaN
    mother_low           -- prior-bar l on inside bars, else NaN
    mother_dir           -- +1 bull / -1 bear / 0 doji, of the mother bar, on inside bars
    active_mother_high   -- armed breakout-up level (ffill, <=5 bars)
    active_mother_low    -- armed breakout-down level (ffill, <=5 bars)
    active_mother_dir    -- armed mother direction (tie-break rule)
    atr                  -- Wilder ATR(14) for the risk layer

No lookahead: inside / mother levels at bar j use bars j-1..j
only; the forward fill only carries levels forward, never future
information.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EXPIRY_BARS = 5  # setup expiry window, fixed a priori (price-action canon)


def add_indicators(df: pd.DataFrame, expiry_bars: int = EXPIRY_BARS) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    o = df["o"]
    c = df["c"]

    # Strict inside: the whole bar (wicks included) inside the prior bar.
    inside = ((h < h.shift(1)) & (l > l.shift(1))).fillna(False)
    df["inside"] = inside.astype(bool)

    mother_h = h.shift(1).where(inside)
    mother_l = l.shift(1).where(inside)
    df["mother_high"] = mother_h
    df["mother_low"] = mother_l
    df["mother_dir"] = (
        np.sign(c.shift(1) - o.shift(1)).where(inside, 0.0).fillna(0.0).astype(int)
    )

    # Armed levels: forward-fill for up to `expiry_bars` bars after the
    # inside bar (the inside bar itself counts as bar 1 of the window);
    # a newer inside bar resets the levels; after the window the setup
    # expires and the levels go back to NaN.
    hv = h.to_numpy()
    lv = l.to_numpy()
    ov = o.to_numpy()
    cv = c.to_numpy()
    in_v = inside.to_numpy()
    n = len(df)
    amh = np.full(n, np.nan)
    aml = np.full(n, np.nan)
    adir = np.zeros(n, dtype=int)
    cur_h, cur_l = np.nan, np.nan
    cur_d = 0
    left = 0
    for i in range(n):
        if in_v[i]:
            cur_h = hv[i - 1]
            cur_l = lv[i - 1]
            d = cv[i - 1] - ov[i - 1]
            cur_d = 1 if d > 0 else (-1 if d < 0 else 0)
            left = expiry_bars
        elif left > 0:
            left -= 1
            if left == 0:
                cur_h, cur_l, cur_d = np.nan, np.nan, 0
        if left > 0:
            amh[i] = cur_h
            aml[i] = cur_l
            adir[i] = cur_d
    df["active_mother_high"] = amh
    df["active_mother_low"] = aml
    df["active_mother_dir"] = adir
    df["atr"] = B.atr(h, l, c, 14)
    return df
