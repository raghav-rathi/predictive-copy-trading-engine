"""RSI pullback to EMA(50) signals.

State machine, one pass:
- Arming: in an uptrend, RSI below 40 arms a long setup; in a
  downtrend, RSI above 60 arms a short setup. Losing the trend
  disarms (the dip only counts if the trend still holds when
  RSI recovers).
- Entry (transition-only): an armed long fires when RSI crosses
  back above 40 while still in an uptrend; an armed short fires
  when RSI crosses back below 60 while still in a downtrend.
  No re-entry while a position is held.
- Exit long: RSI reaches 70 (take the bounce — the pullback
  has run its course) OR close below EMA(50) (the trend that
  justified the trade is gone).
- Exit short: RSI reaches 30 OR close above EMA(50).
- No opposite-side flip: a short setup firing while long does
  not flip the position — the long's own exit rules decide.
  In practice the short setup needs a downtrend, which already
  means close < EMA(50), so the long exit fires on the same bar
  anyway.

All signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    ema50 = df["ema50"].to_numpy(dtype=float)
    rsi = df["rsi"].to_numpy(dtype=float)
    trend_up = df["trend_up"].fillna(False).to_numpy(dtype=bool)
    trend_down = df["trend_down"].fillna(False).to_numpy(dtype=bool)
    cross_up_40 = df["rsi_cross_up_40"].fillna(False).to_numpy(dtype=bool)
    cross_dn_60 = df["rsi_cross_dn_60"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # None | "long" | "short"
    armed_long = False
    armed_short = False
    for i in range(n):
        # 1) exits first (a position held into bar i).
        if pos == "long":
            if rsi[i] >= 70.0 or c[i] < ema50[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if rsi[i] <= 30.0 or c[i] > ema50[i]:
                sx[i] = True
                pos = None
        # 2) entries on the armed setup (transition-only).
        if pos is None:
            if armed_long and cross_up_40[i] and trend_up[i]:
                le[i] = True
                pos = "long"
                armed_long = False
            elif armed_short and cross_dn_60[i] and trend_down[i]:
                se[i] = True
                pos = "short"
                armed_short = False
        # 3) update arming from bar i (after entry, so a cross bar
        #    itself never re-arms).
        if trend_up[i] and rsi[i] < 40.0:
            armed_long = True
        elif not trend_up[i]:
            armed_long = False
        if trend_down[i] and rsi[i] > 60.0:
            armed_short = True
        elif not trend_down[i]:
            armed_short = False

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
