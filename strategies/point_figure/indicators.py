"""Point & Figure 3-box reversal indicators (Dorsey/Wheeler tradition),
implemented in my own words from the documented method.

Box size: 0.5 * ATR(14) per bar (the ATR box-size method). Columns are
built left-to-right from bar closes — strictly causal:

  * an X (rising) column adds a box each time the close rises >= 1 box
    above the column top;
  * it reverses to an O column when the close falls >= 3 boxes from the
    column top (and vice versa for O columns);
  * on reversal the new column is drawn starting 1 box back from the old
    extreme, extending to the current close.

Per-bar columns:
  pf_col (+1 = X, -1 = O), pf_top, pf_bottom,
  pf_prev_x_top (top of the last completed X column),
  pf_prev_o_bottom (bottom of the last completed O column).
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_LEN = 14
BOX_ATR_MULT = 0.5
REVERSAL_BOXES = 3


def _build_pf(closes: np.ndarray, box: np.ndarray) -> dict:
    """Causal P&F column builder. ``closes``/``box`` are 1-D arrays."""
    n = len(closes)
    d = np.zeros(n, dtype=int)
    top = np.full(n, np.nan)
    bot = np.full(n, np.nan)
    prev_x = np.full(n, np.nan)
    prev_o = np.full(n, np.nan)

    cur_dir = 1
    cur_top = closes[0]
    cur_bot = closes[0]
    last_x_top = np.nan
    last_o_bot = np.nan

    for i in range(n):
        b = box[i]
        c = closes[i]
        if np.isfinite(b) and b > 0 and np.isfinite(c):
            if cur_dir == 1:  # X column
                if c >= cur_top + b:
                    cur_top = cur_top + b * int((c - cur_top) // b)
                elif c <= cur_top - REVERSAL_BOXES * b:
                    nboxes = int((cur_top - c) // b)
                    last_x_top = cur_top
                    cur_top = last_x_top - b
                    cur_bot = last_x_top - nboxes * b
                    cur_dir = -1
            else:  # O column
                if c <= cur_bot - b:
                    cur_bot = cur_bot - b * int((cur_bot - c) // b)
                elif c >= cur_bot + REVERSAL_BOXES * b:
                    nboxes = int((c - cur_bot) // b)
                    last_o_bot = cur_bot
                    cur_bot = cur_bot + b
                    cur_top = last_o_bot + nboxes * b
                    cur_dir = 1
        d[i] = cur_dir
        top[i] = cur_top
        bot[i] = cur_bot
        prev_x[i] = last_x_top
        prev_o[i] = last_o_bot
    return {"dir": d, "top": top, "bottom": bot,
            "prev_x_top": prev_x, "prev_o_bottom": prev_o}


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    box = (BOX_ATR_MULT * B.atr(df["h"], df["l"], df["c"], ATR_LEN)).to_numpy()
    pf = _build_pf(df["c"].to_numpy(dtype=float), box)
    df["pf_box"] = box
    df["pf_col"] = pf["dir"]
    df["pf_top"] = pf["top"]
    df["pf_bottom"] = pf["bottom"]
    df["pf_prev_x_top"] = pf["prev_x_top"]
    df["pf_prev_o_bottom"] = pf["prev_o_bottom"]
    return df
