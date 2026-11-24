"""3-bar reversal signals (Joe Ross, "Trading by the Book").

Bullish 3-bar reversal: bar i-2 is a down bar; bar i-1 makes a
lower low than bar i-2 AND closes above bar i-2's close (the hook
back up); bar i closes above bar i-1's high (confirmation).
Bearish mirror: bar i-2 is an up bar; bar i-1 makes a higher high
than bar i-2 AND closes below bar i-2's close; bar i closes below
bar i-1's low.

Exits on the opposite signal (a bearish reversal exits a long, a
bullish reversal exits a short).

CONFIRM modes (calibration knob):
    "high"  -- shipped: bar i closes above bar i-1's high (long)
               / below bar i-1's low (short)
    "close" -- bar i closes above bar i-1's close (long) / below
               bar i-1's close (short) — weaker confirmation
    "none"  -- no confirmation bar: the signal fires on bar i-1
               itself, the moment the hook bar completes

No lookahead: every comparison on bar i uses closes/highs/lows
through bar i only; execution at the next bar's open is the
harness's job.
"""

import pandas as pd

CONFIRM = "high"  # shipped default


def add_signals(df: pd.DataFrame, confirm: str = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    o, h, l, c = df["o"], df["h"], df["l"], df["c"]
    down = df["down_bar"] if "down_bar" in df.columns else c < o
    up = df["up_bar"] if "up_bar" in df.columns else c > o
    ll = df["lower_low"] if "lower_low" in df.columns else l < l.shift(1)
    hh = df["higher_high"] if "higher_high" in df.columns else h > h.shift(1)

    if confirm == "none":
        # hook bar completes on bar i-1 itself; no confirmation bar
        long_entry = (down.shift(1).fillna(False) & ll & (c > c.shift(1))).fillna(False)
        short_entry = (up.shift(1).fillna(False) & hh & (c < c.shift(1))).fillna(False)
    else:
        prev2_down = down.shift(2).fillna(False)
        prev2_up = up.shift(2).fillna(False)
        hook_ll = ll.shift(1).fillna(False)          # bar i-1 lower low vs bar i-2
        hook_hh = hh.shift(1).fillna(False)          # bar i-1 higher high vs bar i-2
        hook_up = c.shift(1) > c.shift(2)            # bar i-1 closes above bar i-2 close
        hook_dn = c.shift(1) < c.shift(2)            # bar i-1 closes below bar i-2 close
        if confirm == "high":
            bull_conf = c > h.shift(1)
            bear_conf = c < l.shift(1)
        elif confirm == "close":
            bull_conf = c > c.shift(1)
            bear_conf = c < c.shift(1)
        else:
            raise ValueError(f"unknown confirm mode: {confirm!r}")
        long_entry = (prev2_down & hook_ll & hook_up & bull_conf).fillna(False)
        short_entry = (prev2_up & hook_hh & hook_dn & bear_conf).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    # exit on the opposite reversal signal
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
