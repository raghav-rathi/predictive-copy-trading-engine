"""Cynthia Kase DevStop -- "Trading with the Odds" (1996).

The DevStop is a volatility stop built from the two-bar true range,
not the one-bar range: a two-bar range catches the gap/extension a
one-bar range misses, so the stop sits far enough out to survive
normal noise but tight enough to cut a real reversal.

    DTR_t       = max(H_t, H_{t-1}) - min(L_t, L_{t-1})
    band_t      = mean(DTR, 30) + 1.0 * stddev(DTR, 30)   (sample std, ddof=1)
    long stop   = ratchet_up(highest high since flip - band)
    short stop  = ratchet_down(lowest low since flip + band)

Direction is a state machine: while long, the stop only ever ratchets
up (running max of highest-high-since-flip minus band); a close below
the long stop flips the state to short, and the short stop then only
ratchets down. The flip IS the entry and the DevStop line IS the exit
-- there is no separate exit rule.

Initial state (documented convention, not a trade): at the first bar
with a valid band the tracker starts in the long state with the stop
set from that bar's high. No entry signal is emitted for the initial
state -- the first trade only fires on a genuine flip. If the market
is falling, the first flip to short arrives within a few bars.

Columns:
    dtr           -- two-bar true range
    devstop_band  -- mean(DTR,30) + std(DTR,30)
    devstop_long  -- long stop line (NaN while short / before warmup)
    devstop_short -- short stop line (NaN while long / before warmup)
    devstop_dir   -- +1 long / -1 short (0 before first valid band)
"""

import numpy as np
import pandas as pd

DTR_N = 30
BAND_STD_MULT = 1.0


def two_bar_range(h: pd.Series, l: pd.Series) -> pd.Series:
    """DTR: max(H_t, H_{t-1}) - min(L_t, L_{t-1})."""
    return pd.concat([h, h.shift(1)], axis=1).max(axis=1) - pd.concat(
        [l, l.shift(1)], axis=1).min(axis=1)


def devstop_band(dtr: pd.Series, n: int = DTR_N,
                 k: float = BAND_STD_MULT) -> pd.Series:
    """mean(DTR, n) + k * sample-stddev(DTR, n)."""
    return dtr.rolling(n, min_periods=n).mean() + k * dtr.rolling(
        n, min_periods=n).std(ddof=1)


def devstop(h: pd.Series, l: pd.Series, c: pd.Series,
            band: pd.Series) -> pd.DataFrame:
    """State-machine DevStop lines and direction.

    Returns devstop_long / devstop_short (NaN when that side is not
    the active state) and devstop_dir (+1 / -1, 0 before warmup).
    """
    h_v = h.to_numpy(dtype=float)
    l_v = l.to_numpy(dtype=float)
    c_v = c.to_numpy(dtype=float)
    b_v = band.to_numpy(dtype=float)
    m = len(c)
    long_stop = np.full(m, np.nan)
    short_stop = np.full(m, np.nan)
    d = np.zeros(m, dtype=float)
    valid = np.where(~np.isnan(b_v))[0]
    if len(valid) == 0:
        return pd.DataFrame(
            {"devstop_long": long_stop, "devstop_short": short_stop,
             "devstop_dir": d}, index=c.index)
    j = valid[0]
    # Initial state: long, stop from this bar's high. No trade signal.
    d[j] = 1.0
    extreme_high = h_v[j]
    long_stop[j] = extreme_high - b_v[j]
    for i in range(j + 1, m):
        if d[i - 1] == 1:
            extreme_high = max(extreme_high, h_v[i])
            cand = extreme_high - b_v[i]
            long_stop[i] = max(long_stop[i - 1], cand)
            if c_v[i] < long_stop[i]:
                # Flip short: new short stop from this bar's low.
                d[i] = -1.0
                extreme_low = l_v[i]
                short_stop[i] = extreme_low + b_v[i]
            else:
                d[i] = 1.0
        else:
            extreme_low = min(extreme_low, l_v[i])
            cand = extreme_low + b_v[i]
            short_stop[i] = min(short_stop[i - 1], cand)
            if c_v[i] > short_stop[i]:
                # Flip long: new long stop from this bar's high.
                d[i] = 1.0
                extreme_high = h_v[i]
                long_stop[i] = extreme_high - b_v[i]
            else:
                d[i] = -1.0
    return pd.DataFrame(
        {"devstop_long": long_stop, "devstop_short": short_stop,
         "devstop_dir": d}, index=c.index)


def add_indicators(df: pd.DataFrame, n: int = DTR_N,
                   k: float = BAND_STD_MULT) -> pd.DataFrame:
    df = df.copy()
    dtr = two_bar_range(df["h"], df["l"])
    band = devstop_band(dtr, n, k)
    st = devstop(df["h"], df["l"], df["c"], band)
    df["dtr"] = dtr
    df["devstop_band"] = band
    df["devstop_long"] = st["devstop_long"]
    df["devstop_short"] = st["devstop_short"]
    df["devstop_dir"] = st["devstop_dir"]
    return df
