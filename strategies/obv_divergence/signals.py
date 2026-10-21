"""OBV divergence signals (Granville, 1963).

Bullish divergence: a new pivot low prints at a lower price than the
previous pivot low, but OBV at the new pivot is higher than OBV at the
previous one — sellers pushed price down but volume pressure stopped
leaking out. Bearish divergence is the mirror at pivot highs.

Divergence between the last two pivots is confirmed at the close of
(pivot_bar + k); the entry fires on the first bar after confirmation.
A divergence signal is skipped if any other divergence signal fired in
the previous 15 bars (dedupe against double-counting one swing).

Exits: a long exits when a new pivot high prints (take the swing — the
counter-trend move is done) or when a bearish divergence confirms.
Shorts mirror. Risk-level exits (stop, trail, max hold) come from
risk.py.

No lookahead: pivots are only readable at their confirmation bar
(b + k); entries fire at b + k + 1. Loops run only over pivot bars
(few), everything else is vectorized.
"""

import numpy as np
import pandas as pd

from strategies.obv_divergence import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = int(df.attrs.get("pivot_k", I.PIVOT_K))
    n = len(df)

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)

    pl_price = df["pivot_low_price"].to_numpy()
    pl_obv = df["pivot_low_obv"].to_numpy()
    ph_price = df["pivot_high_price"].to_numpy()
    ph_obv = df["pivot_high_obv"].to_numpy()

    pl_bars = np.flatnonzero(~np.isnan(pl_price))
    ph_bars = np.flatnonzero(~np.isnan(ph_price))

    last_sig = -10**9

    def _try_entry(bar: int, long: bool) -> None:
        nonlocal last_sig
        if bar < n and bar - last_sig >= 15:
            if long:
                long_entry[bar] = True
            else:
                short_entry[bar] = True
            last_sig = bar

    # --- divergence entries -------------------------------------------------
    for j in range(1, len(pl_bars)):
        a, b = pl_bars[j - 1], pl_bars[j]
        if pl_price[b] < pl_price[a] and pl_obv[b] > pl_obv[a]:
            # bullish divergence: entry on first bar after confirmation
            _try_entry(int(b) + k + 1, long=True)
    for j in range(1, len(ph_bars)):
        a, b = ph_bars[j - 1], ph_bars[j]
        if ph_price[b] > ph_price[a] and ph_obv[b] < ph_obv[a]:
            # bearish divergence
            _try_entry(int(b) + k + 1, long=False)

    # --- swing exits --------------------------------------------------------
    for b in ph_bars:
        x = int(b) + k  # pivot high confirmed -> long swing is done
        if x < n:
            long_exit[x] = True
    for b in pl_bars:
        x = int(b) + k  # pivot low confirmed -> short swing is done
        if x < n:
            short_exit[x] = True
    # bearish divergence also exits a long (confirmed on bar b+k)
    for j in range(1, len(ph_bars)):
        a, b = ph_bars[j - 1], ph_bars[j]
        if ph_price[b] > ph_price[a] and ph_obv[b] < ph_obv[a]:
            x = int(b) + k
            if x < n:
                long_exit[x] = True
    # bullish divergence exits a short
    for j in range(1, len(pl_bars)):
        a, b = pl_bars[j - 1], pl_bars[j]
        if pl_price[b] < pl_price[a] and pl_obv[b] > pl_obv[a]:
            x = int(b) + k
            if x < n:
                short_exit[x] = True

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
