"""Order-block retest signals.

State machine over the indicator columns (causal, one pass):

- Entry: while a block is active, once price has first LEFT the
  block on the displacement side (close above the block high for a
  bullish block, below the block low for a bearish one), a later
  close back INSIDE the block range — while the block is at most
  48 bars old (enforced by the indicator columns going quiet on
  expiry) — enters in the displacement direction. One entry per
  block: after a block has produced an entry, later re-entries into
  the same block do not fire again.
- Exit (long): close below the entry block's low (block violated),
  or a new displacement in the opposite direction (disp_dir == -1).
- Exit (short): mirror — close above the entry block's high, or a
  new bullish displacement (disp_dir == +1).

The harness's 2xATR stop / 2xATR trail / 96-bar max hold do the
trade management beyond these signal exits. All conditions read
bar-j closes at bar j; the harness executes at the next bar's open.
Signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

BLOCK_MAX_AGE = 48  # entry only while the block is at most 48 bars old


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    disp = df["disp_dir"].fillna(0).to_numpy(dtype=int)
    ob_dir = df["ob_dir"].fillna(0).to_numpy(dtype=int)
    ob_low = df["ob_low"].to_numpy(dtype=float)
    ob_high = df["ob_high"].to_numpy(dtype=float)
    ob_age = df["ob_age"].fillna(-1).to_numpy(dtype=int)
    ob_id = df["ob_id"].fillna(-1).to_numpy(dtype=int)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # dict(side, low, high)
    entered_ids = set()
    tracked_id = -1
    left_block = False
    for i in range(n):
        if ob_id[i] != tracked_id:
            tracked_id = ob_id[i]
            left_block = False
        # exits first: a bar can exit an open trade and (below) open
        # the opposite trade only via a fresh block, never the same bar.
        if pos is not None:
            if pos["side"] == "long":
                if c[i] < pos["low"] or disp[i] == -1:
                    lx[i] = True
                    pos = None
            else:
                if c[i] > pos["high"] or disp[i] == 1:
                    sx[i] = True
                    pos = None
        if pos is None and ob_dir[i] != 0 and ob_age[i] <= BLOCK_MAX_AGE:
            d = int(ob_dir[i])
            if (d == 1 and c[i] > ob_high[i]) or (d == -1 and c[i] < ob_low[i]):
                left_block = True
            if (left_block and ob_low[i] <= c[i] <= ob_high[i]
                    and int(ob_id[i]) not in entered_ids):
                entered_ids.add(int(ob_id[i]))
                if d == 1:
                    le[i] = True
                    pos = {"side": "long", "low": ob_low[i], "high": ob_high[i]}
                else:
                    se[i] = True
                    pos = {"side": "short", "low": ob_low[i], "high": ob_high[i]}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
