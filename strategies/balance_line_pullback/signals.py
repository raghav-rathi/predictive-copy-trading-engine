"""Balance Line pullback signals (Bill Williams).

LONG: price pulled back to touch the Balance Line (jaw) --
a bar low inside [jaw - 0.5*ATR, jaw + 0.5*ATR] within the
last 5 bars -- and now turns: close > jaw AND close > prior
close, with the Alligator mouth open up (lips > teeth >
jaw). SHORT mirrors it (bar high touches the jaw, close <
jaw and falling, mouth open down).

The entry fires on the FIRST bar of a run satisfying the
turn condition (condition & ~prior-bar condition), so it
fires once per pullback and never stays True for
consecutive bars while price rides above the jaw. The
turn condition itself is cross-flavoured: a close above
the jaw that was not above it on the prior bar's terms
(the first-bar-of-run guard) -- entries are never plain
level conditions that re-fire every bar.

Exit: long exits when the close crosses BELOW the jaw
(price lost its balance) or the lips cross below the teeth
(mouth closing), or the opposite entry fires; short mirrors.
The house 2xATR hard stop / 3xATR trail sit behind these
exits, and the 96-bar max hold caps a trade that never
resolves.

Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame, require_mouth: bool = True) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    jaw = df["jaw"]
    prev_c = c.shift(1)

    long_cond = (
        df["touch_long_recent"].fillna(False)
        & (c > jaw)
        & (c > prev_c)
    )
    if require_mouth:
        long_cond = long_cond & df["mouth_up"].fillna(False)
    long_cond = long_cond.fillna(False)
    # Fire only on the first bar of a run of the condition.
    long_entry = long_cond & ~long_cond.shift(1).fillna(False)

    short_cond = (
        df["touch_short_recent"].fillna(False)
        & (c < jaw)
        & (c < prev_c)
    )
    if require_mouth:
        short_cond = short_cond & df["mouth_down"].fillna(False)
    short_cond = short_cond.fillna(False)
    short_entry = short_cond & ~short_cond.shift(1).fillna(False)

    # Ambiguous intrabar order: both triggers on one bar -> neither.
    # (A close cannot be both above and below the jaw, so this is
    # a guard, not a live path.)
    both = long_entry & short_entry
    long_entry = long_entry & ~both
    short_entry = short_entry & ~both

    long_exit = (
        crossed_below(c, jaw).fillna(False)
        | crossed_below(df["lips"], df["teeth"]).fillna(False)
        | short_entry
    )
    short_exit = (
        crossed_above(c, jaw).fillna(False)
        | crossed_above(df["lips"], df["teeth"]).fillna(False)
        | long_entry
    )

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
