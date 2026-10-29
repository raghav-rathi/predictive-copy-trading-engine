"""Relative-strength ratio-line breakout signals.

    long_entry  -- ratio breaks above its prior 20-bar high
                   while flat (coin outperforming BTC)
    short_entry -- ratio breaks below its prior 20-bar low
                   while flat (coin underperforming BTC)
    long_exit   -- ratio falls back below its 20-bar mean
                   while long (outperformance faded)
    short_exit  -- ratio rises back above its 20-bar mean
                   while short

State machine: entries only while flat; an exit may be
followed by an opposite entry on the same bar. Boolean
columns, no NaN, no lookahead (the range excludes the
current bar via the shifted rolling window; the SMA uses
only ratios through bar i).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    r = df["ratio"].to_numpy(dtype=float)
    hi = df["ratio_high20"].to_numpy(dtype=float)
    lo = df["ratio_low20"].to_numpy(dtype=float)
    sma = df["ratio_sma20"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and np.isfinite(sma[i]) and r[i] < sma[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and np.isfinite(sma[i]) and r[i] > sma[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if np.isfinite(hi[i]) and r[i] > hi[i]:
                le[i] = True
                pos = "long"
            elif np.isfinite(lo[i]) and r[i] < lo[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df


def add_signals_with_benchmark(df: pd.DataFrame, btc_df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper: indicators + signals with an explicit benchmark."""
    from strategies.relative_strength_breakout import indicators

    return add_signals(indicators.add_indicators(df, benchmark_df=btc_df))
