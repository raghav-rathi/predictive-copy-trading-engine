"""Premium/discount (ICT equilibrium) signals.

Long: close crosses above equilibrium AND the low touched the
discount zone in the last 12 bars — price swept the cheap side
of the range and reclaimed its midpoint, so the discount sweep
is treated as a failed breakdown.

Short mirror: close crosses below equilibrium AND the high
touched the premium zone in the last 12 bars.

Exit: the opposite cross of equilibrium — long exits when close
crosses back below eq, short exits when close crosses back
above eq. Once price loses the midpoint again the premise is
gone; the harness's trail/stop handles the rest.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    eq = df["eq"]
    long_entry = (
        crossed_above(df["c"], eq) & df["touched_discount"].fillna(False)
    ).fillna(False)
    short_entry = (
        crossed_below(df["c"], eq) & df["touched_premium"].fillna(False)
    ).fillna(False)
    long_exit = crossed_below(df["c"], eq).fillna(False)
    short_exit = crossed_above(df["c"], eq).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
