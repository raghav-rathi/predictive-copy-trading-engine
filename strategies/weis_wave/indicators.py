"""David Weis's Weis Wave indicators.

Weis grouped volume by price swing instead of by bar: each "wave" runs
from one swing extreme to the next, and the wave's volume is the sum of
bar volumes inside the wave. A wave that carries much more volume than
the wave before it shows effort; a wave that carries much less shows
effort drying up. (David Weis, "Trades About to Happen", Wiley 2013.)

Swing construction here is strictly causal — bar i uses only data
through bar i's close, so no swing is ever redrawn by later bars:

* Start in an up-wave from the first bar.
* While in an up-wave, the wave high is the max high so far; the wave
  ends (and a down-wave starts) on the first bar whose close falls at
  least REVERSAL below the wave high, where
  REVERSAL = 1.5 * ATR(14) computed causally through the current bar.
* Mirror for down-waves (ends when the close rises at least REVERSAL
  above the wave low).
* The reversal bar is the first bar of the NEW wave: the completed
  wave's volume is the sum of volumes from its start through the bar
  before the reversal bar; the new wave's volume starts at the
  reversal bar's volume. A wave is only "confirmed" when it ends; the
  in-progress wave's volume is provisional.

Columns emitted: ``wave_dir`` (+1 / -1 for the current in-progress
wave), ``wave_vol`` (accumulated volume of the in-progress wave),
``last_completed_wave_vol``, ``prev_completed_wave_vol`` (volumes of
the two most recently completed waves; NaN until that many waves have
completed), plus ``weis_atr`` (the causal ATR(14) used for the
reversal threshold).
"""

import numpy as np
import pandas as pd

from strategies.base import atr

ATR_WINDOW = 14
REVERSAL_ATR_MULT = 1.5
VOLUME_RATIO = 0.85

INDICATOR_COLS = [
    "wave_dir",
    "wave_vol",
    "last_completed_wave_vol",
    "prev_completed_wave_vol",
    "weis_atr",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    wave_dir = np.ones(n, dtype=np.int64)
    wave_vol = np.zeros(n, dtype=float)
    last_completed = np.full(n, np.nan)
    prev_completed = np.full(n, np.nan)

    a = (
        atr(df["h"], df["l"], df["c"], ATR_WINDOW).to_numpy(dtype=float)
        if n
        else np.zeros(0, dtype=float)
    )
    df["weis_atr"] = a
    if n == 0:
        df["wave_dir"] = wave_dir
        df["wave_vol"] = wave_vol
        df["last_completed_wave_vol"] = last_completed
        df["prev_completed_wave_vol"] = prev_completed
        return df

    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)

    direction = 1  # start in an up-wave from the first bar
    wave_high = h[0]
    wave_low = l[0]
    vol = v[0]
    completed: list[tuple[int, float]] = []  # (dir, volume), in completion order

    for i in range(n):
        if i > 0:
            if direction == 1:
                wave_high = max(wave_high, h[i])
                vol += v[i]
                rev = REVERSAL_ATR_MULT * a[i]
                if np.isfinite(rev) and c[i] <= wave_high - rev:
                    # Up-wave completes (bars start..i-1); down-wave starts at i.
                    completed.append((1, vol - v[i]))
                    direction = -1
                    wave_low = l[i]
                    vol = v[i]
            else:
                wave_low = min(wave_low, l[i])
                vol += v[i]
                rev = REVERSAL_ATR_MULT * a[i]
                if np.isfinite(rev) and c[i] >= wave_low + rev:
                    # Down-wave completes (bars start..i-1); up-wave starts at i.
                    completed.append((-1, vol - v[i]))
                    direction = 1
                    wave_high = h[i]
                    vol = v[i]
        wave_dir[i] = direction
        wave_vol[i] = vol
        if len(completed) >= 1:
            last_completed[i] = completed[-1][1]
        if len(completed) >= 2:
            prev_completed[i] = completed[-2][1]

    df["wave_dir"] = wave_dir
    df["wave_vol"] = wave_vol
    df["last_completed_wave_vol"] = last_completed
    df["prev_completed_wave_vol"] = prev_completed
    return df
