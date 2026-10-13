"""Tom DeMark Sequential indicators (The New Science of Technical Analysis, Wiley 1994).

Buy SETUP: 9 consecutive closes with c[j] < c[j-4]. The first bar of a run
(after a bar that broke the chain) is the bearish "price flip" that begins the
setup; any bar with c[j] >= c[j-4] cancels the run.

Buy COUNTDOWN: starts the bar after a completed buy setup. Counts bars where
c[j] <= l[j-2] (non-consecutive OK). Canceled if a sell setup completes while
counting. Completes at 13 bars. QUALIFIER: low of countdown bar 13 must be
<= close of countdown bar 8.

PERFECTION (setup, parameter PERFECT_ONLY): the low of setup bar 8 OR bar 9 is
below the lows of setup bars 6 and 7. With PERFECT_ONLY=True (default) only
perfected setups produce countdown-completion marks.

TDST support = lowest TRUE low (min(low, prior close)) of the 9 buy-setup bars;
TDST resistance = highest TRUE high of the 9 sell-setup bars. Carried forward
until the opposite setup completes.

All marks are causal: bar i's marks use only data through bar i.
"""

import numpy as np
import pandas as pd

SETUP_BARS = 9
COUNTDOWN_BARS = 13
PERFECT_ONLY = True  # require setup perfection for countdown completion marks


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    n = len(df)

    # true range extremes (for TDST)
    tl = np.empty(n)
    th = np.empty(n)
    tl[0] = l[0]
    th[0] = h[0]
    if n > 1:
        tl[1:] = np.minimum(l[1:], c[:-1])
        th[1:] = np.maximum(h[1:], c[:-1])

    buy_setup_done = np.zeros(n, dtype=bool)
    sell_setup_done = np.zeros(n, dtype=bool)
    buy_perfect = np.zeros(n, dtype=bool)
    sell_perfect = np.zeros(n, dtype=bool)
    buy_cd_done = np.zeros(n, dtype=bool)
    sell_cd_done = np.zeros(n, dtype=bool)
    tdst_s = np.full(n, np.nan)
    tdst_r = np.full(n, np.nan)

    run_dn = 0  # consecutive c[j] < c[j-4]
    run_up = 0  # consecutive c[j] > c[j-4]
    last_tdst_s = np.nan
    last_tdst_r = np.nan

    # countdown state: +1 = buy countdown active, -1 = sell, 0 = idle
    cd_side = 0
    cd_count = 0
    cd_bar8_close = np.nan
    cd_perfect = False

    for i in range(n):
        # ---- setups ----
        if i >= 4:
            if c[i] < c[i - 4]:
                run_dn += 1
                run_up = 0
            elif c[i] > c[i - 4]:
                run_up += 1
                run_dn = 0
            else:
                run_dn = 0
                run_up = 0
        if run_dn == SETUP_BARS:
            buy_setup_done[i] = True
            # perfection: 1-indexed setup bars 8/9 lows vs bars 6/7 lows
            b6, b7, b8, b9 = l[i - 3], l[i - 2], l[i - 1], l[i]
            buy_perfect[i] = (b8 < b6 and b8 < b7) or (b9 < b6 and b9 < b7)
            last_tdst_s = float(tl[i - 8 : i + 1].min())
        elif run_up == SETUP_BARS:
            sell_setup_done[i] = True
            b6, b7, b8, b9 = h[i - 3], h[i - 2], h[i - 1], h[i]
            sell_perfect[i] = (b8 > b6 and b8 > b7) or (b9 > b6 and b9 > b7)
            last_tdst_r = float(th[i - 8 : i + 1].max())

        tdst_s[i] = last_tdst_s
        tdst_r[i] = last_tdst_r

        # ---- countdowns ----
        if buy_setup_done[i]:
            # new buy setup restarts (cancels any active) countdown
            cd_side, cd_count, cd_perfect = 1, 0, bool(buy_perfect[i])
            cd_bar8_close = np.nan
        elif sell_setup_done[i]:
            cd_side, cd_count, cd_perfect = -1, 0, bool(sell_perfect[i])
            cd_bar8_close = np.nan
        elif cd_side != 0 and i >= 2 and c[i] <= l[i - 2]:
            cd_count += 1
            if cd_count == 8:
                cd_bar8_close = c[i]
            if cd_count == COUNTDOWN_BARS:
                qualified = bool(l[i] <= cd_bar8_close)
                ok = qualified and (cd_perfect or not PERFECT_ONLY)
                if cd_side == 1:
                    buy_cd_done[i] = ok
                else:
                    sell_cd_done[i] = ok
                # countdown over; a new one needs a new setup
                cd_side, cd_count = 0, 0

    df["buy_setup_done"] = buy_setup_done
    df["sell_setup_done"] = sell_setup_done
    df["buy_perfect"] = buy_perfect
    df["sell_perfect"] = sell_perfect
    df["buy_cd_done"] = buy_cd_done
    df["sell_cd_done"] = sell_cd_done
    df["tdst_s"] = tdst_s
    df["tdst_r"] = tdst_r
    return df
