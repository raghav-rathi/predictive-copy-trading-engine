"""Fakey signals (Nial Fuller).

Mother bar i-2; inside bar i-1 (high < mother high AND low >
mother low). On bar i:

    Bullish fakey: bar i breaks BELOW the inside bar's low
    (low[i] < low[i-1]) but closes back inside the mother bar's
    range (close[i] > low[i-2]) -> long. The downside break was
    fake; trapped shorts fuel the move up.
    Bearish fakey: bar i breaks ABOVE the inside bar's high
    (high[i] > high[i-1]) but closes back inside the mother
    bar's range (close[i] < high[i-2]) -> short.

Exit on the opposite signal — a fakey the other way is the
premise expiring (the range has now genuinely broken the other
way). A bar that breaks BOTH sides of the inside bar while
closing inside the mother range is ambiguous and fires neither
entry.

``confirm`` selects the close-back-inside range:
    "mother" (shipped): close back inside the mother bar's range
    "inside": close back inside the inside bar's range only
    (close[i] > low[i-1] for bullish / close[i] < high[i-1]
    for bearish) — a stricter confirmation that demands the
    break bar fully reclaim the inside bar.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

CONFIRM = "mother"  # shipped default


def add_signals(df: pd.DataFrame, confirm: str = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]

    inside_prev = (h.shift(1) < h.shift(2)) & (l.shift(1) > l.shift(2))

    if confirm == "inside":
        bull_close = c > l.shift(1)
        bear_close = c < h.shift(1)
    else:  # "mother"
        bull_close = c > l.shift(2)
        bear_close = c < h.shift(2)

    bull = (inside_prev & (l < l.shift(1)) & bull_close).fillna(False)
    bear = (inside_prev & (h > h.shift(1)) & bear_close).fillna(False)
    # a wide-range bar can break BOTH sides of the inside bar while
    # closing inside the mother range — that is not a fakey in either
    # direction, so an ambiguous bar fires neither entry
    both = bull & bear
    bull = bull & ~both
    bear = bear & ~both

    df["long_entry"] = bull.astype(bool)
    df["short_entry"] = bear.astype(bool)
    df["long_exit"] = bear.astype(bool)
    df["short_exit"] = bull.astype(bool)
    return df
