"""Larry Williams Oops signals, bar-based.

The Oops idea: an opening gap against the prior day's range is an
overreaction; the "oops" is satisfied when price reverses back through
the prior day's extreme -- the buy stop just above the prior day's low
(or sell stop just below the prior day's high) gets hit.

    long_entry  = first bar within `session` bars of a gap_down bar
                  whose close is back above *that gap bar's*
                  prev_day_low (the stop level is pinned, like the
                  original's buy stop just above the prior day's low)
    short_entry = first bar within `session` bars of a gap_up bar
                  whose close is back below that gap bar's prev_day_high

At most one entry per gap (the stop triggers once). Entries are only
allowed on the first session after the gap: if price never reclaims
the pinned extreme within `session` bars, the setup expires.

    long_exit  = short_entry   (the opposite Oops signal)
    short_exit = long_entry

"Session end" exits are handled by the risk layer: max_hold_bars=24
flattens the position one session after entry, matching Williams'
intraday flat-by-close design.

Signal columns are boolean, no NaN, no lookahead (every quantity on
bar j uses data through bar j only; the harness executes at the next
bar's open).
"""

import numpy as np
import pandas as pd

SESSION = 24  # must match indicators.SESSION shipped default


def _first_reclaim(
    gap: pd.Series, level: pd.Series, close: pd.Series, session: int,
    above: bool,
) -> pd.Series:
    """Boolean series: first reclaim bar after each gap bar.

    For every bar i where ``gap`` is True, mark the first bar j in
    [i, i + session - 1] where ``close`` is back through the level
    pinned at bar i (``level[i]``): above it for longs, below it for
    shorts. At most one entry per gap. Uses only data known at each
    bar -- no lookahead.
    """
    out = np.zeros(len(gap), dtype=bool)
    g = gap.to_numpy()
    lv = level.to_numpy(dtype=float)
    cl = close.to_numpy(dtype=float)
    for i in np.flatnonzero(g):
        if not np.isfinite(lv[i]):
            continue
        crossed = cl[i : i + session] > lv[i] if above else cl[i : i + session] < lv[i]
        hits = np.flatnonzero(crossed)
        if hits.size:
            out[i + hits[0]] = True
    return pd.Series(out, index=gap.index)


def add_signals(df: pd.DataFrame, session: int = SESSION) -> pd.DataFrame:
    df = df.copy()
    gap_d = df["gap_down"].fillna(False).astype(bool)
    gap_u = df["gap_up"].fillna(False).astype(bool)

    long_entry = _first_reclaim(gap_d, df["prev_day_low"], df["c"],
                                session, above=True)
    short_entry = _first_reclaim(gap_u, df["prev_day_high"], df["c"],
                                 session, above=False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    # Opposite Oops signal exits the position; session-end exit comes
    # from risk.max_hold_bars.
    df["long_exit"] = df["short_entry"].copy()
    df["short_exit"] = df["long_entry"].copy()
    return df
