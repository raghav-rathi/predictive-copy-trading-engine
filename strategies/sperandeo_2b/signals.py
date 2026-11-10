"""Sperandeo 2B false-breakout reversal signals.

2B Top (short): (1) a new 20-bar high; (2) a pullback of at least
3 bars with no new 20-bar high; (3) a later bar (the breakout bar)
closes above that 20-bar high; (4) a subsequent bar closes below
the breakout bar's low -- that close is the short_entry signal.
2B Bottom (long) is the exact mirror.

State machine, per side, all causal (bar i uses only data through
bar i's close):
  idle -> armed: a new 20-bar extreme is recorded.
  armed -> armed (reset): a newer 20-bar extreme forms; the pullback
      counter restarts from the new extreme.
  armed -> awaiting_failure: after >= 3 pullback bars (bars with no
      new 20-bar extreme), a bar closes beyond the extreme
      (above the 20-bar high / below the 20-bar low). That bar is
      the breakout bar; its low (top) / high (bottom) is recorded.
      Note the breakout bar itself usually prints a new 20-bar high
      (its high exceeds the old extreme), so the breakout check runs
      before the newer-extreme reset while armed with >= 3 pullback
      bars.
  awaiting_failure -> idle (signal): a bar closes beyond the
      breakout bar's low (top) / high (bottom). That close fires
      short_entry / long_entry.
  awaiting_failure -> armed (reset): price makes a new 20-bar
      extreme beyond the breakout bar's extreme -- the breakout is
      holding, the pattern is invalidated, and the new extreme
      starts a fresh pattern.

Only the most recent qualifying 20-bar extreme is tracked. A signal
exits the opposite side: a 2B Top (short_entry) is also long_exit,
and a 2B Bottom (long_entry) is also short_exit.
"""

import numpy as np
import pandas as pd

LOOKBACK = 20
MIN_PULLBACK_BARS = 3


def _detect_2b(h, l, c, is_new_high, is_new_low):
    """Run the 2B state machine. Returns (long_entry, short_entry) bool arrays."""
    n = len(c)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    # Top-side state.
    top_state = "idle"  # idle | armed | awaiting_failure
    top_extreme = np.nan  # the 20-bar high being tested
    top_pullback = 0  # bars since the extreme with no new 20-bar high
    top_breakout_low = np.nan  # low of the breakout bar

    # Bottom-side state (mirror).
    bot_state = "idle"
    bot_extreme = np.nan
    bot_pullback = 0
    bot_breakout_high = np.nan

    for i in range(n):
        hi = float(h[i])
        lo = float(l[i])
        cl = float(c[i])
        new_high = bool(is_new_high[i])
        new_low = bool(is_new_low[i])

        # --- Top side (short) ---
        if top_state == "idle":
            if new_high:
                top_state = "armed"
                top_extreme = hi
                top_pullback = 0
        elif top_state == "armed":
            if top_pullback >= MIN_PULLBACK_BARS and cl > top_extreme:
                # Breakout bar: closes above the 20-bar high.
                top_state = "awaiting_failure"
                top_breakout_low = lo
            elif new_high:
                # Newer 20-bar extreme: restart the pattern from it.
                top_extreme = hi
                top_pullback = 0
            else:
                top_pullback += 1
        else:  # awaiting_failure
            if cl < top_breakout_low:
                short_entry[i] = True
                top_state = "idle"
                top_extreme = np.nan
                top_pullback = 0
                top_breakout_low = np.nan
            elif new_high and hi > top_extreme:
                # Breakout holding and extending: new extreme, fresh pattern.
                top_state = "armed"
                top_extreme = hi
                top_pullback = 0
                top_breakout_low = np.nan

        # --- Bottom side (long), exact mirror ---
        if bot_state == "idle":
            if new_low:
                bot_state = "armed"
                bot_extreme = lo
                bot_pullback = 0
        elif bot_state == "armed":
            if bot_pullback >= MIN_PULLBACK_BARS and cl < bot_extreme:
                bot_state = "awaiting_failure"
                bot_breakout_high = hi
            elif new_low:
                bot_extreme = lo
                bot_pullback = 0
            else:
                bot_pullback += 1
        else:  # awaiting_failure
            if cl > bot_breakout_high:
                long_entry[i] = True
                bot_state = "idle"
                bot_extreme = np.nan
                bot_pullback = 0
                bot_breakout_high = np.nan
            elif new_low and lo < bot_extreme:
                bot_state = "armed"
                bot_extreme = lo
                bot_pullback = 0
                bot_breakout_high = np.nan

    return long_entry, short_entry


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    is_new_high = df["is_new_high"].fillna(False).to_numpy(dtype=bool)
    is_new_low = df["is_new_low"].fillna(False).to_numpy(dtype=bool)
    long_entry, short_entry = _detect_2b(h, l, c, is_new_high, is_new_low)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    # Exit on the opposite 2B pattern.
    df["long_exit"] = short_entry
    df["short_exit"] = long_entry
    return df
