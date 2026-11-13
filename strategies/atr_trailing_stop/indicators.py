"""ATR trailing-stop (Chandelier Exit family) indicators.

Chuck LeBeau's Chandelier Exit hangs a trailing stop off the extreme
price reached since the current regime began:

    long stop  = highest high since the long regime started - 3 * ATR(14)
    short stop = lowest low since the short regime started + 3 * ATR(14)

The stop only ever ratchets in the regime's favour (up for longs, down
for shorts): a rising ATR without a new extreme never loosens it.
When the close crosses the stop, the regime flips and the anchor
resets to that bar's low (new short regime) or high (new long regime).

Columns:

    atr           -- Wilder ATR(14)
    chand_anchor  -- running extreme since the regime started
                    (highest high in a long regime, lowest low in a
                    short regime)
    chand_stop    -- the trailing stop line
    chand_dir     -- +1 long regime / -1 short regime (NaN before the
                    first bar with a valid ATR)

No lookahead: every value on bar i uses data through bar i's close.
The regime state is carried forward causally, one bar at a time.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
MULT = 3.0

INDICATOR_COLS = ["atr", "chand_anchor", "chand_stop", "chand_dir"]


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N,
                   mult: float = MULT) -> pd.DataFrame:
    df = df.copy()
    atr = B.atr(df["h"], df["l"], df["c"], atr_n)
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    a = atr.to_numpy()
    n = len(df)

    anchor = np.full(n, np.nan)
    stop = np.full(n, np.nan)
    direction = np.full(n, np.nan)

    valid = np.where(np.isfinite(a))[0]
    if len(valid) == 0:
        df["atr"] = atr
        df["chand_anchor"] = anchor
        df["chand_stop"] = stop
        df["chand_dir"] = direction
        return df

    j = int(valid[0])
    # Seed the first regime from the first valid bar: anchor on its
    # high, stop 3 ATR below; the close decides the starting regime.
    anchor[j] = h[j]
    stop[j] = h[j] - mult * a[j]
    direction[j] = 1.0 if c[j] >= stop[j] else -1.0
    if direction[j] == -1.0:
        anchor[j] = l[j]
        stop[j] = l[j] + mult * a[j]

    for i in range(j + 1, n):
        if not np.isfinite(a[i]):
            anchor[i] = anchor[i - 1]
            stop[i] = stop[i - 1]
            direction[i] = direction[i - 1]
            continue
        if direction[i - 1] == 1.0:
            new_anchor = max(anchor[i - 1], h[i])
            raw_stop = new_anchor - mult * a[i]
            # Ratchet: the stop only ever moves up in a long regime.
            new_stop = max(stop[i - 1], raw_stop)
            if c[i] < new_stop:
                # Regime flips short: anchor resets to this bar's low.
                direction[i] = -1.0
                anchor[i] = l[i]
                stop[i] = l[i] + mult * a[i]
            else:
                direction[i] = 1.0
                anchor[i] = new_anchor
                stop[i] = new_stop
        else:
            new_anchor = min(anchor[i - 1], l[i])
            raw_stop = new_anchor + mult * a[i]
            # Ratchet: the stop only ever moves down in a short regime.
            new_stop = min(stop[i - 1], raw_stop)
            if c[i] > new_stop:
                # Regime flips long: anchor resets to this bar's high.
                direction[i] = 1.0
                anchor[i] = h[i]
                stop[i] = h[i] - mult * a[i]
            else:
                direction[i] = -1.0
                anchor[i] = new_anchor
                stop[i] = new_stop

    df["atr"] = atr
    df["chand_anchor"] = anchor
    df["chand_stop"] = stop
    df["chand_dir"] = direction
    return df
