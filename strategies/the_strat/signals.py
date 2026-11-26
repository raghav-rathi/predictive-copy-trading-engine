"""The Strat setup signals.

Setups (classes read off the trigger bar and the bars before
it; the entry signal fires on the close of the trigger bar,
the final 2 bar, and the harness enters at the next-bar open):

    2-1-2 reversal:     2D, 1, 2U -> long | 2U, 1, 2D -> short
    3-1-2 reversal:     3, 1, 2U  -> long | 3, 1, 2D  -> short
    2-2 reversal:       2D, 2U    -> long | 2U, 2D    -> short
    2-1-2 continuation: 2U, 1, 2U -> long | 2D, 1, 2D -> short

Every setup is gated by FTFC: longs only when the daily AND
weekly directions are both green (+1), shorts only when both
are red (-1). A flat or unknown FTFC direction blocks the
entry.

Exits: a long exits on the opposite setup (any short setup
firing), a short exits on any long setup — the Strat's own
reversal is the exit. The exit is NOT FTFC-gated: once a
position is open, the opposite setup is a reversal signal
regardless of the higher time frames. The harness 2xATR
stop / 3xATR trail / 120-bar max hold sit behind the signal
exit.

Adaptation note: the book's entry is a break of the trigger
bar's high/low (a stop order above/below the 2 bar). On
close-based 1h bars the trigger is only known at the close,
so the signal fires on the trigger bar's close and the
harness enters at the next bar's open — the same adaptation
every close-based system in this repo makes.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

# strat_class codes: 1 = inside, 2 = 2U, -2 = 2D, 3 = outside


def _setup_long(cls: pd.Series) -> pd.Series:
    c0 = cls.shift(2)  # two bars ago
    c1 = cls.shift(1)  # one bar ago
    c2 = cls         # trigger bar
    rev_212 = (c0 == -2) & (c1 == 1) & (c2 == 2)
    rev_312 = (c0 == 3) & (c1 == 1) & (c2 == 2)
    rev_22 = (c1 == -2) & (c2 == 2)
    cont_212 = (c0 == 2) & (c1 == 1) & (c2 == 2)
    return rev_212 | rev_312 | rev_22 | cont_212


def _setup_short(cls: pd.Series) -> pd.Series:
    c0 = cls.shift(2)
    c1 = cls.shift(1)
    c2 = cls
    rev_212 = (c0 == 2) & (c1 == 1) & (c2 == -2)
    rev_312 = (c0 == 3) & (c1 == 1) & (c2 == -2)
    rev_22 = (c1 == 2) & (c2 == -2)
    cont_212 = (c0 == -2) & (c1 == 1) & (c2 == -2)
    return rev_212 | rev_312 | rev_22 | cont_212


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cls = df["strat_class"]
    setup_long = _setup_long(cls)
    setup_short = _setup_short(cls)
    ftfc_long = (df["ftfc_daily"] == 1) & (df["ftfc_weekly"] == 1)
    ftfc_short = (df["ftfc_daily"] == -1) & (df["ftfc_weekly"] == -1)
    df["long_entry"] = (setup_long & ftfc_long).fillna(False).astype(bool)
    df["short_entry"] = (setup_short & ftfc_short).fillna(False).astype(bool)
    # Opposite setup exits the open position (not FTFC-gated).
    df["long_exit"] = setup_short.fillna(False).astype(bool)
    df["short_exit"] = setup_long.fillna(False).astype(bool)
    return df
