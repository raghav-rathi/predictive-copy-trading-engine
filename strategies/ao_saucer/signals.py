"""Bill Williams AO Saucer signals.

BUY saucer on bar i (all three AO bars above zero):
    ao[i] > 0, ao[i-1] > 0, ao[i-2] > 0,
    ao[i-1] < ao[i-2] (red: AO falling) and
    ao[i] > ao[i-1] (green: AO rising again).
The saucer completes on bar i -- a turn from red to green
above zero. SELL saucer is the mirror below zero.

Exits (shipped, exit_mode="zero"): a long exits on
crossed_below(ao, 0) OR on a sell saucer; a short exits on
crossed_above(ao, 0) OR on a buy saucer. A saucer that
closes one side opens the other, so a buy saucer both exits
a short and enters a long (executed at next-bar open by the
harness).

Calibration variant exit_mode="two_bar": the zero-cross exit
is replaced by an exit on two consecutive AO bars in the
adverse direction (two red bars for a long, two green bars
for a short); the opposite-saucer exit is kept in both modes.

Calibration variant strict=False ("relaxed"): only ao[i] and
ao[i-1] are required on the saucer's side of zero; the
ao[i-2] requirement is dropped. NOTE: this is provably
identical to strict -- ao[i-1] > 0 together with the turn
ao[i-1] < ao[i-2] forces ao[i-2] > 0 (mirror for sells), so
the relaxed sweep must reproduce the shipped numbers
exactly. See CALIBRATION.md.

Signal columns are boolean, no NaN, no lookahead. Entries
are discrete pattern completions (a red-to-green AO turn),
not level conditions: a saucer fires on one bar only and
cannot re-fire while AO keeps rising.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below


def _saucer(ao: np.ndarray, strict: bool = True):
    """Return (buy_saucer, sell_saucer) boolean arrays."""
    n = len(ao)
    buy = np.zeros(n, dtype=bool)
    sell = np.zeros(n, dtype=bool)
    for i in range(2, n):
        a0, a1, a2 = ao[i - 2], ao[i - 1], ao[i]
        if not (np.isfinite(a0) and np.isfinite(a1) and np.isfinite(a2)):
            continue
        # Buy saucer: turn red -> green, above zero.
        if a2 > 0 and a1 > 0 and a1 < a0 and a2 > a1:
            if strict:
                if a0 > 0:
                    buy[i] = True
            else:
                buy[i] = True
        # Sell saucer: turn green -> red, below zero.
        if a2 < 0 and a1 < 0 and a1 > a0 and a2 < a1:
            if strict:
                if a0 < 0:
                    sell[i] = True
            else:
                sell[i] = True
    return buy, sell


def add_signals(
    df: pd.DataFrame,
    strict: bool = True,
    exit_mode: str = "zero",
) -> pd.DataFrame:
    if exit_mode not in ("zero", "two_bar"):
        raise ValueError(f"unknown exit_mode {exit_mode!r}")
    df = df.copy()
    n = len(df)
    ao = df["ao"].to_numpy(float)
    buy, sell = _saucer(ao, strict=strict)

    if exit_mode == "zero":
        zero_down = crossed_below(df["ao"], 0).fillna(False).to_numpy(bool)
        zero_up = crossed_above(df["ao"], 0).fillna(False).to_numpy(bool)
        long_exit = zero_down | sell
        short_exit = zero_up | buy
    else:  # two_bar: two consecutive adverse AO bars
        two_red = np.zeros(n, dtype=bool)
        two_green = np.zeros(n, dtype=bool)
        for i in range(2, n):
            if np.isfinite(ao[i]) and np.isfinite(ao[i - 1]) and np.isfinite(ao[i - 2]):
                two_red[i] = ao[i] < ao[i - 1] and ao[i - 1] < ao[i - 2]
                two_green[i] = ao[i] > ao[i - 1] and ao[i - 1] > ao[i - 2]
        long_exit = two_red | sell
        short_exit = two_green | buy

    df["long_entry"] = buy
    df["short_entry"] = sell
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
