"""Inside bar breakout signals: trade the expansion out of contraction.

    long_entry  = close crosses ABOVE the armed mother_high
    short_entry = close crosses BELOW the armed mother_low

Crosses are evaluated with ``strategies.base.crossed_above/below``
against the forward-filled armed levels, so a signal on bar j uses
only data through bar j's close; the harness executes at the next
bar's open. The armed levels are NaN once the setup expires, and
crosses against NaN are always False -- an expired setup can never
fire.

Tie-break: if both crosses fired on the same bar (only possible
when a newer inside bar re-armed and jumped the levels intrabar),
take the direction of the mother bar -- bull mother prefers long,
bear mother prefers short.

Exits are signal-driven: the opposite breakout exits the position
(long_exit = short_entry, short_exit = long_entry), in addition to
the ATR stop / 2R target / max-hold risk layer in risk.py.

Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    mh = df["active_mother_high"]
    ml = df["active_mother_low"]

    up = crossed_above(c, mh).fillna(False)
    dn = crossed_below(c, ml).fillna(False)
    mdir = df["active_mother_dir"].fillna(0)

    # Tie-break: both crosses on the same bar (re-armed level jump) ->
    # follow the mother bar's direction; bull/flat prefers long.
    both = up & dn
    long_entry = ((up & ~dn) | (both & (mdir >= 0))).fillna(False).astype(bool)
    short_entry = ((dn & ~up) | (both & (mdir < 0))).fillna(False).astype(bool)

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    # Opposite breakout exits the position.
    df["long_exit"] = df["short_entry"].copy()
    df["short_exit"] = df["long_entry"].copy()
    return df
