"""Alligator + Awesome Oscillator indicators (Bill Williams Profitunity).

Alligator: Wilder-smoothed moving averages (SMMA) of the median
price (H+L)/2 -- Jaw 13, Teeth 8, Lips 5. SMMA[i] =
(SMMA[i-1]*(n-1) + price[i]) / n, seeded with the simple average
of the first n prices (first valid value at index n-1).

DEVIATION, documented: the book displaces the Alligator lines
8/5/3 bars into the future for plotting. Those shifted values
are used causally here -- UNSHIFTED SMMA values. Using the
forward displacement in a live signal would be lookahead
(it needs future bars); the displacement is a charting
convention, not a trading rule.

Awesome Oscillator: AO = SMA(median, 5) - SMA(median, 34).
AO "green" when AO > previous AO, "red" when AO < previous AO.

Fractals: an up-fractal at bar i requires h[i] to be the
strict maximum of h[i-2..i+2]; a down-fractal mirrors on the
lows. A fractal is only confirmed once the 2 bars after it
close, so the fractal column is set True at bar i+2 (causal,
no lookahead) and carries the fractal bar's high/low as its
level. The most recent confirmed fractal level is
forward-filled (frac_*_level_ff) so a later close can be
judged against it.

Columns:
    median, jaw, teeth, lips, ao, ao_green, ao_red
    frac_up, frac_up_level, frac_up_level_ff
    frac_down, frac_down_level, frac_down_level_ff

No lookahead: SMMA/SMA are causal recursions, fractals are
confirmed with a 2-bar lag, and every column at bar i uses
only bars through i.
"""

import numpy as np
import pandas as pd

JAW_N = 13
TEETH_N = 8
LIPS_N = 5
AO_FAST = 5
AO_SLOW = 34
FRAC_N = 2


def smma(s, n: int):
    """Wilder-smoothed moving average.

    SMMA[i] = (SMMA[i-1]*(n-1) + price[i]) / n, seeded with the
    simple average of the first n prices (first valid value at
    index n-1). NaN before that.
    """
    vals = s.to_numpy(float)
    out = np.full(len(vals), np.nan)
    if len(vals) >= n:
        out[n - 1] = vals[:n].mean()
        for i in range(n, len(vals)):
            out[i] = (out[i - 1] * (n - 1) + vals[i]) / n
    return pd.Series(out, index=s.index)


def add_indicators(
    df: pd.DataFrame,
    jaw_n: int = JAW_N,
    teeth_n: int = TEETH_N,
    lips_n: int = LIPS_N,
    ao_fast: int = AO_FAST,
    ao_slow: int = AO_SLOW,
    frac_n: int = FRAC_N,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    df["median"] = median
    df["jaw"] = smma(median, jaw_n)
    df["teeth"] = smma(median, teeth_n)
    df["lips"] = smma(median, lips_n)
    ao = df["median"].rolling(ao_fast, min_periods=ao_fast).mean() - df[
        "median"
    ].rolling(ao_slow, min_periods=ao_slow).mean()
    df["ao"] = ao
    df["ao_green"] = (ao > ao.shift(1)).fillna(False)
    df["ao_red"] = (ao < ao.shift(1)).fillna(False)

    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    n = len(df)
    frac_up = np.zeros(n, dtype=bool)
    frac_up_level = np.full(n, np.nan)
    frac_down = np.zeros(n, dtype=bool)
    frac_down_level = np.full(n, np.nan)
    for i in range(frac_n, n - frac_n):
        lo, hi = i - frac_n, i + frac_n + 1
        window_h = h[lo:hi]
        if h[i] == window_h.max() and int((window_h == h[i]).sum()) == 1:
            frac_up[i + frac_n] = True
            frac_up_level[i + frac_n] = h[i]
        window_l = l[lo:hi]
        if l[i] == window_l.min() and int((window_l == l[i]).sum()) == 1:
            frac_down[i + frac_n] = True
            frac_down_level[i + frac_n] = l[i]
    df["frac_up"] = frac_up
    df["frac_up_level"] = frac_up_level
    df["frac_down"] = frac_down
    df["frac_down_level"] = frac_down_level
    df["frac_up_level_ff"] = pd.Series(frac_up_level, index=df.index).ffill()
    df["frac_down_level_ff"] = pd.Series(
        frac_down_level, index=df.index
    ).ffill()
    return df
