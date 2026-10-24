"""ICT/SMC order-block detection (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Displacement: a 3-bar close-to-close move of at least 1.5xATR(14)
   in one direction, ending at bar i:

       bullish: c[i] - c[i-3] >= 1.5 * atr[i]
       bearish: c[i] - c[i-3] <= -1.5 * atr[i]

   A move that size in three bars is the "displacement leg" — the
   footprint of aggressive institutional flow, not drift.

2. Order block: the range (low..high) of the LAST opposite-color
   candle before the displacement leg, scanning back from bar i-3
   (the base bar of the move) up to 20 bars. Bullish displacement
   wants the last bearish candle (close < open); bearish wants the
   last bullish candle (close > open). If no opposite-color candle
   is found in the scan window, no block forms.

3. The block stays active for 48 bars from the displacement bar.
   A newer displacement replaces the active block (latest block
   wins). After 48 bars the block expires and the columns go quiet.

Columns:

    disp_dir -- +1 bullish displacement bar, -1 bearish, 0 otherwise
    ob_dir   -- +1 while a bullish block is active, -1 bearish, else 0
    ob_low   -- active block low (NaN when no block active)
    ob_high  -- active block high (NaN when no block active)
    ob_age   -- bars since the displacement bar (-1 when inactive)
    ob_id    -- incrementing id of the active block (-1 when inactive)
    atr      -- Wilder ATR(14)

No lookahead: displacement, block scan, and expiry all read bars
<= i. The loop is sequential, so appending later bars cannot change
earlier rows.
"""

import numpy as np
import pandas as pd

from strategies import base as B

DISP_BARS = 3          # displacement move measured over 3 bars
DISP_ATR_MULT = 1.5    # displacement must be >= 1.5xATR
SCAN_BACK = 20         # bars scanned back for the opposite-color candle
BLOCK_MAX_AGE = 48     # block expires 48 bars after displacement


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    atr = B.atr(df["h"], df["l"], df["c"], 14).to_numpy(dtype=float)

    disp_dir = np.zeros(n, dtype=int)
    ob_dir = np.zeros(n, dtype=int)
    ob_low = np.full(n, np.nan)
    ob_high = np.full(n, np.nan)
    ob_age = np.full(n, -1, dtype=int)
    ob_id = np.full(n, -1, dtype=int)

    active = None  # dict(dir, low, high, disp_bar, id)
    next_id = 0
    for i in range(n):
        d = 0
        if i >= DISP_BARS and np.isfinite(atr[i]) and atr[i] > 0:
            move = c[i] - c[i - DISP_BARS]
            thr = DISP_ATR_MULT * atr[i]
            if move >= thr:
                d = 1
            elif move <= -thr:
                d = -1
        disp_dir[i] = d
        if d != 0:
            blk = None
            lo = max(-1, i - DISP_BARS - SCAN_BACK)
            for j in range(i - DISP_BARS, lo - 1, -1):
                if d == 1 and c[j] < o[j]:
                    blk = (l[j], h[j])
                    break
                if d == -1 and c[j] > o[j]:
                    blk = (l[j], h[j])
                    break
            if blk is not None:
                active = {"dir": d, "low": blk[0], "high": blk[1],
                          "disp_bar": i, "id": next_id}
                next_id += 1
        if active is not None:
            age = i - active["disp_bar"]
            if age <= BLOCK_MAX_AGE:
                ob_dir[i] = active["dir"]
                ob_low[i] = active["low"]
                ob_high[i] = active["high"]
                ob_age[i] = age
                ob_id[i] = active["id"]
            else:
                active = None

    df["disp_dir"] = disp_dir
    df["ob_dir"] = ob_dir
    df["ob_low"] = ob_low
    df["ob_high"] = ob_high
    df["ob_age"] = ob_age
    df["ob_id"] = ob_id
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
