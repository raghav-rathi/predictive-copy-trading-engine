"""Bill Williams MFI squat-bar breakout signals.

Squat breakout: remember the most recent SQUAT bar (its high/low).
Only the most recent squat counts; a newer squat replaces it.

  Long entry:  a bar closes above the squat bar's high within the
               next 5 bars after the squat (the squat bar itself is
               excluded), AND the close is above EMA(20).
  Short entry: a bar closes below the squat bar's low within the
               next 5 bars, AND the close is below EMA(20).

Exits (applied by the harness only while the matching side is open):

  Long exit:  a FADE bar (MFI down + volume down = interest fading),
              or a close below EMA(20).
  Short exit: a FADE bar, or a close above EMA(20).

All inputs are computed from data through bar i's close, so signals
on bar i use no future data. A squat is not consumed by an entry:
if the position exits while the same squat is still inside its
5-bar window, a fresh breakout close can re-enter (see
CALIBRATION.md).
"""

import numpy as np
import pandas as pd

SQUAT_WINDOW = 5  # bars after the squat bar during which a breakout counts


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    ema20 = df["ema20"].to_numpy(dtype=float)
    bar_type = df["bar_type"].to_numpy()

    squat_high = np.nan
    squat_low = np.nan
    squat_idx = -1

    for i in range(n):
        # Breakout vs the most recent squat (age 1..5 bars; the squat
        # bar itself is excluded). Checked BEFORE the current bar can
        # replace the stored squat.
        if squat_idx >= 0 and 1 <= i - squat_idx <= SQUAT_WINDOW:
            e = ema20[i]
            if np.isfinite(e):
                if c[i] > squat_high and c[i] > e:
                    long_entry[i] = True
                elif c[i] < squat_low and c[i] < e:
                    short_entry[i] = True
        # A newer squat replaces the stored one.
        if bar_type[i] == "squat":
            squat_high = h[i]
            squat_low = l[i]
            squat_idx = i

    is_fade = bar_type == "fade"
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = (is_fade | (c < ema20)).astype(bool)
    df["short_exit"] = (is_fade | (c > ema20)).astype(bool)
    return df
