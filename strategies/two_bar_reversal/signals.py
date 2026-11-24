"""2-bar key reversal signals (Larry Williams, "Long-Term Secrets
to Short-Term Trading").

Bullish key reversal: bar i-1 is a down bar (close < open) AND
makes a lower low than bar i-2, AND bar i closes above bar i-1's
high (confirmation). Bearish mirror: bar i-1 is an up bar making
a higher high than bar i-2, AND bar i closes below bar i-1's low.

Exits on the opposite signal (a bearish reversal exits a long, a
bullish reversal exits a short).

CONFIRM modes (calibration knob):
    "high"  -- shipped: bar i closes above bar i-1's high (long)
               / below bar i-1's low (short)
    "close" -- bar i closes above bar i-1's close (long) / below
               bar i-1's close (short) — weaker confirmation
    "none"  -- no confirmation bar: the signal fires on bar i-1
               itself, the moment the down-bar + lower-low (or
               up-bar + higher-high) pattern completes

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
        # pattern completes on bar i-1 itself; no confirmation bar
        long_entry = (down & ll).fillna(False)
        short_entry = (up & hh).fillna(False)
    else:
        prev_down = down.shift(1).fillna(False)
        prev_ll = ll.shift(1).fillna(False)
        prev_up = up.shift(1).fillna(False)
        prev_hh = hh.shift(1).fillna(False)
        if confirm == "high":
            bull_conf = c > h.shift(1)
            bear_conf = c < l.shift(1)
        elif confirm == "close":
            bull_conf = c > c.shift(1)
            bear_conf = c < c.shift(1)
        else:
            raise ValueError(f"unknown confirm mode: {confirm!r}")
        long_entry = (prev_down & prev_ll & bull_conf).fillna(False)
        short_entry = (prev_up & prev_hh & bear_conf).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    # exit on the opposite reversal signal
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
