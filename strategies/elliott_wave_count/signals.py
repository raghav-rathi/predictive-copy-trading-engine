"""Elliott wave-count signals.

A strict, mechanical wave counter over the confirmed 5-bar pivots.
Hard rules (all enforced, no discretionary relabelling):

    * wave 2 retraces 38.2-61.8% of wave 1 (and never 100%+)
    * wave 3 is never the shortest -- checked when wave 3 completes
      (at the wave-4 pivot): if wave-3 length < wave-1 length the
      count is invalid and the trade exits
    * wave 4 never overlaps wave-1 territory -- a close inside
      wave-1's range after entry is an invalidation exit
    * wave 5 target is the 161.8% extension of wave 1

    long_entry  -- valid waves 1-2 counted (retracement in band),
                   enter on a close above the wave-1 high (wave-3
                   breakout)
    short_entry -- mirror image (close below the wave-1 low)
    long_exit   -- wave 4 enters wave-1 territory (close below the
                   wave-1 high), or the wave-5 target (161.8%
                   extension) is reached, or wave 3 turns out
                   shorter than wave 1, or price falls under the
                   wave-4 low
    short_exit  -- mirror image

State machine (one setup at a time; states are latched, not derived
from the last three pivots, so a lower high after wave 2 does not
silently disarm the setup):

    0  idle -- waiting for a wave-1 pivot pair (low then high, or
       high then low)
    +/-1  have wave 1, waiting for wave 2 (a pivot retracing
       38.2-61.8% of wave 1)
    +/-2  armed -- valid waves 1-2, waiting for the wave-3 breakout
    +/-3  in wave 3 -- tracking the wave-3 extreme, waiting for the
       wave-4 pivot (long: a swing low / short: a swing high)
    +/-4  in wave 5 -- wave 4 confirmed valid, waiting for the
       161.8% extension target

Caveat (by design): live wave counts are ambiguous and the strict
rules prune most candidates, so this strategy trades rarely.  The
backtest trade count is reported honestly in BACKTEST.md.

Every decision on bar i uses pivots/closes through bar i only; the
harness executes at bar i+1's open, so there is no lookahead.
"""

import numpy as np
import pandas as pd

RETR_LO = 0.382  # shipped wave-2 retracement band, lower edge
RETR_HI = 0.618  # shipped wave-2 retracement band, upper edge
EXT = 1.618      # shipped wave-5 target: 161.8% extension of wave 1

# state codes: sign = direction (+ long / - short)
S_IDLE = 0
S_W1 = 1       # have wave 1, waiting for wave 2
S_ARMED = 2    # valid waves 1-2, waiting for wave-3 breakout
S_W3 = 3       # in wave 3, waiting for the wave-4 pivot
S_W5 = 4       # in wave 5, waiting for the 161.8% target


def _wave_states(df: pd.DataFrame, retr_lo: float = RETR_LO,
                 retr_hi: float = RETR_HI, ext: float = EXT) -> pd.DataFrame:
    """Walk the pivots; return per-bar wave state + entry/exit flags."""
    n = len(df)
    sh = df["swing_high"].to_numpy(dtype=float)
    sl = df["swing_low"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)

    state = np.zeros(n, dtype=int)
    w1_hi = np.full(n, np.nan)
    w1_lo = np.full(n, np.nan)
    w2 = np.full(n, np.nan)
    w5_tgt = np.full(n, np.nan)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)

    st = S_IDLE
    # wave-1 / wave-2 candidate levels (direction follows sign of st)
    a_lo = np.nan  # wave-1 low  (long: start of wave 1)
    a_hi = np.nan  # wave-1 high (long: end of wave 1)
    a_w2 = np.nan  # wave-2 extreme (long: low / short: high)
    w3_ext = np.nan  # running wave-3 extreme (long: high / short: low)
    w4_ext = np.nan  # confirmed wave-4 extreme
    tgt = np.nan
    # most recent pivot, for wave-1 pair detection while idle
    last_kind = ""   # "H" or "L"
    last_price = np.nan

    def _retr_long(lo, hi, x):
        return (hi - x) / (hi - lo) if hi > lo else np.nan

    def _retr_short(hi, lo, x):
        return (x - lo) / (hi - lo) if hi > lo else np.nan

    for i in range(n):
        # ---- swing-high pivot arrivals --------------------------------------
        if not np.isnan(sh[i]):
            p = sh[i]
            if st == S_IDLE:
                if last_kind == "L" and p > last_price:
                    a_lo, a_hi = last_price, p  # wave 1 (long) formed
                    st = S_W1
            elif st == S_W1:
                if p > a_hi:
                    a_hi = p  # wave 1 extends upward
            elif st == S_ARMED:
                if p > a_hi:
                    # wave 1 extends after arming: re-check the stored
                    # wave 2 against the wider wave 1
                    r = _retr_long(a_lo, p, a_w2)
                    a_hi = p
                    if not (retr_lo <= r <= retr_hi):
                        st = S_W1  # extended wave 1 needs a fresh wave 2
            elif st == -S_W3:
                # wave-4 high candidate (short): overlap + shortest checks
                if p >= a_lo:
                    short_exit[i] = True  # wave 4 overlaps wave-1 territory
                    st = S_IDLE
                else:
                    w3_len = a_w2 - w3_ext
                    w1_len = a_hi - a_lo
                    if w3_len < w1_len:
                        short_exit[i] = True  # wave 3 shortest: invalid
                        st = S_IDLE
                    else:
                        w4_ext = p
                        tgt = a_lo - ext * w1_len
                        st = -S_W5
            last_kind, last_price = "H", p

        # ---- swing-low pivot arrivals ---------------------------------------
        if not np.isnan(sl[i]):
            p = sl[i]
            if st == S_IDLE:
                if last_kind == "H" and p < last_price:
                    a_hi, a_lo = last_price, p  # wave 1 (short) formed
                    st = -S_W1
            elif st == -S_W1:
                if p < a_lo:
                    a_lo = p  # wave 1 extends downward
            elif st == -S_ARMED:
                if p < a_lo:
                    r = _retr_short(a_hi, p, a_w2)
                    a_lo = p
                    if not (retr_lo <= r <= retr_hi):
                        st = -S_W1
            elif st == S_W3:
                # wave-4 low candidate (long): overlap + shortest checks
                if p <= a_hi:
                    long_exit[i] = True  # wave 4 overlaps wave-1 territory
                    st = S_IDLE
                else:
                    w3_len = w3_ext - a_w2
                    w1_len = a_hi - a_lo
                    if w3_len < w1_len:
                        long_exit[i] = True  # wave 3 shortest: invalid
                        st = S_IDLE
                    else:
                        w4_ext = p
                        tgt = a_hi + ext * w1_len
                        st = S_W5
            last_kind, last_price = "L", p

        # ---- wave-2 arrivals --------------------------------------------------
        # long setup: wave 2 is a swing low; short setup: a swing high
        if not np.isnan(sl[i]) and st == S_W1:
            r = _retr_long(a_lo, a_hi, sl[i])
            if retr_lo <= r <= retr_hi:
                a_w2 = sl[i]
                st = S_ARMED
            elif r > 1.0:
                st = S_IDLE  # wave 2 erased wave 1: count restarts
            # 0.618 < r <= 1.0: wave 2 too deep for the shipped band;
            # keep waiting -- a deeper low later can still qualify.
        if not np.isnan(sh[i]) and st == -S_W1:
            r = _retr_short(a_hi, a_lo, sh[i])
            if retr_lo <= r <= retr_hi:
                a_w2 = sh[i]
                st = -S_ARMED
            elif r > 1.0:
                st = S_IDLE
        if not np.isnan(sl[i]) and st == S_ARMED:
            # wave 2 deepens while armed: re-check the band
            r = _retr_long(a_lo, a_hi, sl[i])
            if retr_lo <= r <= retr_hi:
                a_w2 = sl[i]
            else:
                st = S_W1  # out of band: back to waiting for a wave 2
        if not np.isnan(sh[i]) and st == -S_ARMED:
            r = _retr_short(a_hi, a_lo, sh[i])
            if retr_lo <= r <= retr_hi:
                a_w2 = sh[i]
            else:
                st = -S_W1

        # ---- close-driven transitions ---------------------------------------
        if st == S_ARMED and c[i] > a_hi:
            long_entry[i] = True
            w3_ext = h[i]
            st = S_W3
        elif st == -S_ARMED and c[i] < a_lo:
            short_entry[i] = True
            w3_ext = l[i]
            st = -S_W3
        elif st == S_W3:
            w3_ext = max(w3_ext, h[i])
            if c[i] < a_hi:
                long_exit[i] = True  # breakout failed / overlap
                st = S_IDLE
        elif st == -S_W3:
            w3_ext = min(w3_ext, l[i])
            if c[i] > a_lo:
                short_exit[i] = True
                st = S_IDLE
        elif st == S_W5:
            if c[i] >= tgt:
                long_exit[i] = True  # wave-5 target reached
                st = S_IDLE
            elif c[i] < a_hi or c[i] < w4_ext:
                long_exit[i] = True  # invalidation / structure failure
                st = S_IDLE
        elif st == -S_W5:
            if c[i] <= tgt:
                short_exit[i] = True
                st = S_IDLE
            elif c[i] > a_lo or c[i] > w4_ext:
                short_exit[i] = True
                st = S_IDLE

        state[i] = st
        if st != S_IDLE:
            w1_hi[i], w1_lo[i] = a_hi, a_lo
            if st not in (S_W1, -S_W1):
                w2[i] = a_w2
            if st in (S_W5, -S_W5):
                w5_tgt[i] = tgt

    return pd.DataFrame(
        {"ew_state": state, "ew_w1_hi": w1_hi, "ew_w1_lo": w1_lo,
         "ew_w2": w2, "ew_w5_target": w5_tgt,
         "long_entry": long_entry, "short_entry": short_entry,
         "long_exit": long_exit, "short_exit": short_exit},
        index=df.index)


def add_signals(df: pd.DataFrame, retr_lo: float = RETR_LO,
                retr_hi: float = RETR_HI, ext: float = EXT) -> pd.DataFrame:
    df = df.copy()
    st = _wave_states(df, retr_lo=retr_lo, retr_hi=retr_hi, ext=ext)
    for col in st.columns:
        df[col] = st[col]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
