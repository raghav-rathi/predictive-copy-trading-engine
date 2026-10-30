"""Classic Point & Figure (Dorsey) columns built causally from closes.

Box size = 1% of the current price level, recomputed ONLY when a new
column starts, so boxes are stable within a column (per spec). A column
of X's tracks rising prices, a column of O's falling prices. A 3-box
reversal flips the column: from an X column, a close at least 3 boxes
below the column high starts an O column; from an O column, a close at
least 3 boxes above the column low starts an X column. On a flip the box
size is recomputed as 1% of the reversal bar's close.

Signals (StockCharts basic P&F signals):
  * double-top breakout: an X column's high exceeds the high of the
    previous X column -> pf_signal = +1 on the bar the new high is set.
  * double-bottom breakdown: an O column's low goes below the low of
    the previous O column -> pf_signal = -1 on that bar.
  * reversal: pf_reversal = True on the bar a new column starts.
Only closes are used (classic P&F uses price, not time), so intraday
highs/lows inside a bar do not create boxes; the bar's close is the
price that either extends the column, flips it, or does nothing.
Everything is causal: bar i uses closes through i only.

Columns:
    pf_dir      -- +1 in an X column, -1 in an O column, 0 before any
                   column has formed
    pf_box      -- box size in force on that bar
    pf_col_high -- high of the current column so far
    pf_col_low  -- low of the current column so far
    pf_signal   -- +1 double-top breakout, -1 double-bottom breakdown
    pf_reversal -- True on a column-flip bar
    atr         -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

BOX_FRAC = 0.01
REVERSAL_BOXES = 3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    direction = np.zeros(n, dtype=int)
    box = np.zeros(n, dtype=float)
    col_high = np.zeros(n, dtype=float)
    col_low = np.zeros(n, dtype=float)
    signal = np.zeros(n, dtype=int)
    reversal = np.zeros(n, dtype=bool)
    if n == 0:
        df["pf_dir"] = direction
        df["pf_box"] = box
        df["pf_col_high"] = col_high
        df["pf_col_low"] = col_low
        df["pf_signal"] = signal
        df["pf_reversal"] = reversal
        df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
        return df

    cur_box = BOX_FRAC * c[0]
    d = 0  # 0 = no column yet, +1 = X, -1 = O
    ch = c[0]
    cl = c[0]
    prev_x_high = np.nan
    prev_o_low = np.nan
    for i in range(n):
        ci = c[i]
        if d == 0:
            if ci >= ch + cur_box:
                d = 1
                ch = ci
            elif ci <= cl - cur_box:
                d = -1
                cl = ci
        elif d == 1:
            if ci > ch:
                old = ch
                ch = ci
                if np.isfinite(prev_x_high) and old <= prev_x_high < ch:
                    signal[i] = 1
            elif ci <= ch - REVERSAL_BOXES * cur_box:
                prev_x_high = ch
                d = -1
                cl = ci
                cur_box = BOX_FRAC * ci
                reversal[i] = True
                if np.isfinite(prev_o_low) and ci < prev_o_low:
                    signal[i] = -1
        else:  # d == -1
            if ci < cl:
                old = cl
                cl = ci
                if np.isfinite(prev_o_low) and old >= prev_o_low > cl:
                    signal[i] = -1
            elif ci >= cl + REVERSAL_BOXES * cur_box:
                prev_o_low = cl
                d = 1
                ch = ci
                cur_box = BOX_FRAC * ci
                reversal[i] = True
                if np.isfinite(prev_x_high) and ci > prev_x_high:
                    signal[i] = 1
        direction[i] = d
        box[i] = cur_box
        col_high[i] = ch
        col_low[i] = cl

    df["pf_dir"] = direction
    df["pf_box"] = box
    df["pf_col_high"] = col_high
    df["pf_col_low"] = col_low
    df["pf_signal"] = signal
    df["pf_reversal"] = reversal
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
