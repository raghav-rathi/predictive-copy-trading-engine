"""Original Turtle entries/exits with the System-1 skip rule.

System 1 (20-bar breakout):
    long_entry_s1  = close > dc20_high.shift(1)
    short_entry_s1 = close < dc20_low.shift(1)
    ... skipped when the previous *completed* System-1 trade in the same
    direction was a winner (the Turtles' skip rule).

System 2 (55-bar failsafe): taken only when flat, the last System-1
signal in the same direction was skipped, and the close breaks the
55-bar channel -- always taken once those hold.

Exits: System-1 positions exit on the 10-bar opposite-channel cross,
System-2 on the 20-bar cross. The 2N stop is enforced by the backtest
harness via RiskConfig (stop_atr_mult=2.0, atr_window=20).

The skip rule needs the *outcome* of the last System-1 trade, so this
module runs a lightweight internal simulator over the signal bars:
entries at the next bar's open, exits on the system's channel cross or
the 2N stop (max 500 bars), mirroring the harness's execution timing
exactly (stop checked intrabar from the bar after entry, channel-exit
signal on bar x exits at the open of bar x+1, re-entry evaluated on the
same signal bar the harness would use). Winner = gross PnL > 0. One
position at a time -- no pyramiding, so while a position is open no new
entry signals are evaluated, and only completed System-1 trades update
the skip-rule state.

Output columns (boolean, no NaN): long_entry, short_entry, long_exit,
short_exit -- the merged standard columns -- plus long_entry_s1,
short_entry_s1, long_entry_s2, short_entry_s2, and a `system` tag column
('S1'/'S2' on entry-signal bars, '' elsewhere; each exit belongs to the
currently open position's system).
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.turtle_classic.risk import WARMUP

STOP_MULT = 2.0   # 2N stop -- matches RiskConfig.stop_atr_mult
MAX_HOLD = 500    # matches RiskConfig.max_hold_bars


def _raw_arrays(df: pd.DataFrame) -> dict:
    """Raw breakout / channel-cross flags as numpy bool arrays."""
    c = df["c"]

    def flag(s: pd.Series) -> np.ndarray:
        return s.fillna(False).to_numpy().astype(bool)

    return {
        # entries: breakout bar's close vs the channel known before it
        "s1l": flag(c > df["dc20_high"].shift(1)),
        "s1s": flag(c < df["dc20_low"].shift(1)),
        "s2l": flag(c > df["dc55_high"].shift(1)),
        "s2s": flag(c < df["dc55_low"].shift(1)),
        # exits: opposite-channel crosses
        "x1l": flag(crossed_below(c, df["exit10_low"].shift(1))),
        "x1s": flag(crossed_above(c, df["exit10_high"].shift(1))),
        "x2l": flag(crossed_below(c, df["exit20_low"].shift(1))),
        "x2s": flag(crossed_above(c, df["exit20_high"].shift(1))),
    }


def _simulate_trade(o, h, l, c, x_long, x_short, side, j, n, N):
    """Simulate one trade entered at the open of bar j+1.

    Returns (resume_j, outcome, exit_signal_bar, reason, exit_exec_bar)
    where resume_j is the next signal-bar index the outer walk should
    evaluate, outcome is 'win'/'loss' by gross PnL sign, exit_signal_bar
    is the bar whose channel-cross fired (None for stop/max-hold exits),
    reason is 'stop'/'channel'/'max_hold'/'eod', and exit_exec_bar is the
    bar the exit executes on.
    """
    e = j + 1
    entry = float(o[e])
    is_long = side == "long"
    stop = entry - STOP_MULT * N if is_long else entry + STOP_MULT * N
    x_sig = x_long if is_long else x_short
    last = min(e + MAX_HOLD, n - 1)

    def scored(px):
        win = (px > entry) if is_long else (px < entry)
        return "win" if win else "loss"

    for i in range(e, last + 1):
        # 1) 2N stop, intrabar from the bar after entry (the harness only
        #    checks the stop once the position exists, i.e. from bar e+1)
        if i > e:
            if is_long and l[i] <= stop:
                return i - 1, scored(min(stop, o[i])), None, "stop", i
            if not is_long and h[i] >= stop:
                return i - 1, scored(max(stop, o[i])), None, "stop", i
        # 2) max hold (harness exits at the open, before the signal check)
        if i - e >= MAX_HOLD:
            return i - 1, scored(float(o[i])), None, "max_hold", i
        # 3) channel cross on bar i -> exit at the next open
        if x_sig[i]:
            if i + 1 < n:
                return i, scored(float(o[i + 1])), i, "channel", i + 1
            return n, scored(float(c[i])), i, "eod", i
    return n, scored(float(c[last])), None, "eod", last


def generate(df: pd.DataFrame, use_s2: bool = True, use_skip: bool = True,
             warmup: int = WARMUP):
    """Build signal columns + the internal trade list.

    Returns (frame, trades). ``trades`` is a list of dicts with system,
    side, entry_bar (signal bar), entry_px, exit_bar (execution bar),
    exit_signal_bar, outcome, reason -- exposed for tests.
    """
    raw = _raw_arrays(df)
    o = df["o"].to_numpy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    atr_arr = df["atr"].to_numpy()
    n = len(df)

    le_s1 = np.zeros(n, bool)
    se_s1 = np.zeros(n, bool)
    le_s2 = np.zeros(n, bool)
    se_s2 = np.zeros(n, bool)
    lx = np.zeros(n, bool)
    sx = np.zeros(n, bool)
    system = np.array([""] * n, dtype=object)

    last = {"long": None, "short": None}      # last completed S1 outcome
    skipped = {"long": False, "short": False}  # pending S1 skip per side
    trades = []

    j = 0
    while j < n - 1:
        if j < warmup - 1:
            j += 1
            continue
        N = atr_arr[j]
        atr_ok = bool(np.isfinite(N) and N > 0)
        took = None

        # --- longs: S1 first, then the S2 failsafe ---
        if raw["s1l"][j]:
            if use_skip and last["long"] == "win":
                skipped["long"] = True
            elif atr_ok:
                took = ("S1", "long")
                skipped["long"] = False
        if took is None and use_s2 and raw["s2l"][j] and skipped["long"] and atr_ok:
            took = ("S2", "long")
            skipped["long"] = False

        # --- shorts (only while still flat) ---
        if took is None:
            if raw["s1s"][j]:
                if use_skip and last["short"] == "win":
                    skipped["short"] = True
                elif atr_ok:
                    took = ("S1", "short")
                    skipped["short"] = False
            if took is None and use_s2 and raw["s2s"][j] and skipped["short"] and atr_ok:
                took = ("S2", "short")
                skipped["short"] = False

        if took is None:
            j += 1
            continue

        sys_, side = took
        is_long = side == "long"
        if sys_ == "S1":
            if is_long:
                le_s1[j] = True
            else:
                se_s1[j] = True
        else:
            if is_long:
                le_s2[j] = True
            else:
                se_s2[j] = True
        system[j] = sys_

        x_long = raw["x1l"] if sys_ == "S1" else raw["x2l"]
        x_short = raw["x1s"] if sys_ == "S1" else raw["x2s"]
        resume, outcome, exit_sig_bar, reason, exit_exec = _simulate_trade(
            o, h, l, c, x_long, x_short, side, j, n, float(N))
        entry_px = float(o[j + 1])
        if exit_sig_bar is not None:
            if is_long:
                lx[exit_sig_bar] = True
            else:
                sx[exit_sig_bar] = True
        if sys_ == "S1" and reason != "eod":
            # only completed trades feed the skip rule; a trade still
            # open at the data edge has no outcome yet
            last[side] = outcome
        trades.append({
            "system": sys_,
            "side": side,
            "entry_bar": j,
            "entry_px": entry_px,
            "exit_bar": exit_exec,
            "exit_signal_bar": exit_sig_bar,
            "outcome": outcome,
            "reason": reason,
        })
        j = resume if resume > j else j + 1

    frame = df.copy()
    frame["long_entry_s1"] = le_s1
    frame["short_entry_s1"] = se_s1
    frame["long_entry_s2"] = le_s2
    frame["short_entry_s2"] = se_s2
    frame["long_entry"] = le_s1 | le_s2
    frame["short_entry"] = se_s1 | se_s2
    frame["long_exit"] = lx
    frame["short_exit"] = sx
    frame["system"] = system
    return frame, trades


def add_signals(df: pd.DataFrame, use_s2: bool = True, use_skip: bool = True,
                warmup: int = WARMUP) -> pd.DataFrame:
    """Shipped entry point: full S1+S2 original rules. ``use_s2`` /
    ``use_skip`` / ``warmup`` overrides exist for tests and the
    CALIBRATION.md S1-only sweep."""
    frame, _ = generate(df, use_s2=use_s2, use_skip=use_skip, warmup=warmup)
    return frame
