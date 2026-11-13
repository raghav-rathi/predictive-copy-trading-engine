"""RSI(14) hidden-divergence signals (trend continuation).

Hidden divergence compares *consecutive* swing pivots:

    Bullish hidden: price makes a HIGHER swing low while RSI makes a
                    LOWER low at that pivot  -> long.
    Bearish hidden: price makes a LOWER swing high while RSI makes a
                    HIGHER high at that pivot -> short.

(Regular divergence — lower price low + higher RSI low — is the
reversal setup and is deliberately NOT traded here.)

A pivot at bar j is confirmed at bar j+2, so the entry fires on the
confirmation bar (j+2), using only the pivot bar's own price and RSI
values plus the previous pivot's. Nothing is read from bars after
the signal bar.

    Long entry:  bullish hidden divergence confirmed.
    Short entry: bearish hidden divergence confirmed.
    Long exit:   RSI crosses below 50.
    Short exit:  RSI crosses above 50.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies; the
RSI-50 cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import numpy as np
import pandas as pd

from strategies import base as B

EXIT_LEVEL = 50.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    rsi = df["rsi"].to_numpy(dtype=float)
    low = df["l"].to_numpy(dtype=float)
    high = df["h"].to_numpy(dtype=float)
    pivot_low = df["pivot_low"].fillna(False).to_numpy(dtype=bool)
    pivot_high = df["pivot_high"].fillna(False).to_numpy(dtype=bool)

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    last_low = None   # (price, rsi) of the previous confirmed swing low
    last_high = None  # (price, rsi) of the previous confirmed swing high

    for i in range(n):
        j = i - 2  # the pivot confirmed on this bar
        if j >= 0:
            if pivot_low[j] and np.isfinite(rsi[j]):
                if last_low is not None:
                    prev_price, prev_rsi = last_low
                    if (np.isfinite(prev_rsi)
                            and low[j] > prev_price
                            and rsi[j] < prev_rsi):
                        long_entry[i] = True
                last_low = (low[j], rsi[j])
            if pivot_high[j] and np.isfinite(rsi[j]):
                if last_high is not None:
                    prev_price, prev_rsi = last_high
                    if (np.isfinite(prev_rsi)
                            and high[j] < prev_price
                            and rsi[j] > prev_rsi):
                        short_entry[i] = True
                last_high = (high[j], rsi[j])

    long_exit = B.crossed_below(df["rsi"], EXIT_LEVEL)
    short_exit = B.crossed_above(df["rsi"], EXIT_LEVEL)
    df["long_entry"] = pd.Series(long_entry, index=df.index)
    df["short_entry"] = pd.Series(short_entry, index=df.index)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
