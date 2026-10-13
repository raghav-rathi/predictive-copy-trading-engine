"""Holy Grail signals (Raschke & Connors, Street Smarts Ch.10).

Long:  ADX(14) > 30 and rising with +DI > -DI; wait for a pullback bar whose
       low touches the 20 EMA (low <= ema20, prior close above it); arm a buy
       stop above the touch bar's high; enter when a later bar's high takes it
       out. Protective stop = swing low = lowest low from the touch bar through
       the breakout bar (fixed, emitted as long_exit on a close below it).
Short: mirror (high touches EMA from below, sell stop below touch low, stop at
       swing high).

One signal per ADX turn-up: after a trade fires from a turn-up, no new touch
may arm until ADX turns up above 30 again.

Timing approximation (documented): the touch bar is identified at its close;
the breakout is detected on the breakout bar's high, so the signal fires on
the breakout bar and the harness fills at the NEXT bar's open — one bar later
than a true buy-stop fill. Exits use the same bar-close/next-open convention.
"""

import numpy as np
import pandas as pd

ADX_MIN = 30.0
ADX_EXIT = 25.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    adx = df["adx"].to_numpy(dtype=float)
    adx_prev = df["adx_prev"].to_numpy(dtype=float)
    pdi = df["plus_di"].to_numpy(dtype=float)
    mdi = df["minus_di"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    ema = df["ema20"].to_numpy(dtype=float)
    n = len(df)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    armed = None  # (side, touch_bar, trigger_px); side +1 long / -1 short
    traded_long = False   # a long fired since the last long turn-up
    traded_short = False
    prev_up_ok = False
    prev_dn_ok = False
    in_pos = 0            # mirrors the harness position: +1 / -1 / 0
    swing = np.nan        # fixed protective level for the open trade

    for i in range(n):
        rising = adx[i] > adx_prev[i]
        up_ok = adx[i] > ADX_MIN and rising and pdi[i] > mdi[i]
        dn_ok = adx[i] > ADX_MIN and rising and mdi[i] > pdi[i]
        if up_ok and not prev_up_ok:
            traded_long = False  # ADX turned up: re-arm long setups
        if dn_ok and not prev_dn_ok:
            traded_short = False

        if in_pos == 1:
            if c[i] < swing or adx[i] < ADX_EXIT:
                lx[i] = True
                in_pos = 0
        elif in_pos == -1:
            if c[i] > swing or adx[i] < ADX_EXIT:
                sx[i] = True
                in_pos = 0
        else:
            # flat: manage the armed touch
            if armed is not None:
                side, tb, trig = armed
                if side == 1:
                    if not up_ok:
                        armed = None  # trend gate lost: drop the stop
                    elif h[i] > trig:
                        le[i] = True
                        in_pos = 1
                        swing = float(np.min(l[tb : i + 1]))
                        traded_long = True
                        armed = None
                else:
                    if not dn_ok:
                        armed = None
                    elif l[i] < trig:
                        se[i] = True
                        in_pos = -1
                        swing = float(np.max(h[tb : i + 1]))
                        traded_short = True
                        armed = None
            # touch detection (only when flat and nothing armed)
            if armed is None and i > 0:
                if up_ok and not traded_long and l[i] <= ema[i] and c[i - 1] > ema[i - 1]:
                    armed = (1, i, float(h[i]))
                elif dn_ok and not traded_short and h[i] >= ema[i] and c[i - 1] < ema[i - 1]:
                    armed = (-1, i, float(l[i]))

        prev_up_ok = up_ok
        prev_dn_ok = dn_ok

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
