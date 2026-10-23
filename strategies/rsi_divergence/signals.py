"""RSI(14) divergence signals on confirmed swing pivots.

Divergence is measured between the last two *confirmed* swing pivots,
comparing the price pivot against the RSI(14) value at the same pivot
bars. A pivot centered at bar p is confirmed at the close of bar p+k,
so the signal on the confirmation bar uses only data known at that
bar's close; the harness executes at the next bar's open.

    Regular bullish: price lower low  AND rsi higher low  -> long_entry
    Hidden bullish:  price higher low AND rsi lower low   -> long_entry
    Regular bearish: price higher high AND rsi lower high -> short_entry
    Hidden bearish:  price lower high  AND rsi higher high -> short_entry

Each confirmed pivot pair fires at most once: the signal is set on the
confirmation bar of the *second* (newly confirmed) pivot, and the pair
is never revisited.

Exits: a long exits when any bearish divergence (regular or hidden)
confirms; a short exits when any bullish divergence confirms. ATR
stop / chandelier trail / max-hold exits come from risk.py.

Signal columns are boolean, no NaN, no lookahead. Loops run only over
pivot bars (few); everything else is vectorized.
"""

import numpy as np
import pandas as pd

from strategies.rsi_divergence import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = int(df.attrs.get("pivot_k", I.PIVOT_LEFT))
    n = len(df)

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)

    pl_price = df["pivot_low_price"].to_numpy()
    pl_rsi = df["pivot_low_rsi"].to_numpy()
    ph_price = df["pivot_high_price"].to_numpy()
    ph_rsi = df["pivot_high_rsi"].to_numpy()

    pl_bars = np.flatnonzero(~np.isnan(pl_price))
    ph_bars = np.flatnonzero(~np.isnan(ph_price))

    # --- bullish divergences (pivot lows) -> long entries / short exits ---
    for j in range(1, len(pl_bars)):
        a, b = int(pl_bars[j - 1]), int(pl_bars[j])
        c = b + k  # confirmation bar of the newly confirmed pivot
        if c >= n:
            continue
        if np.isnan(pl_rsi[a]) or np.isnan(pl_rsi[b]):
            continue
        if pl_price[b] < pl_price[a] and pl_rsi[b] > pl_rsi[a]:
            long_entry[c] = True    # regular bullish
            short_exit[c] = True
        elif pl_price[b] > pl_price[a] and pl_rsi[b] < pl_rsi[a]:
            long_entry[c] = True    # hidden bullish (trend continuation)
            short_exit[c] = True

    # --- bearish divergences (pivot highs) -> short entries / long exits ---
    for j in range(1, len(ph_bars)):
        a, b = int(ph_bars[j - 1]), int(ph_bars[j])
        c = b + k
        if c >= n:
            continue
        if np.isnan(ph_rsi[a]) or np.isnan(ph_rsi[b]):
            continue
        if ph_price[b] > ph_price[a] and ph_rsi[b] < ph_rsi[a]:
            short_entry[c] = True   # regular bearish
            long_exit[c] = True
        elif ph_price[b] < ph_price[a] and ph_rsi[b] > ph_rsi[a]:
            short_entry[c] = True   # hidden bearish (trend continuation)
            long_exit[c] = True

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
