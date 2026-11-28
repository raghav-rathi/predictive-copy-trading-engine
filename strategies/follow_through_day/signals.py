"""Follow-Through Day signals.

Long: the close crosses ABOVE 0.5 on the 0/1 ftd_day flag --
i.e. the single 23:00 bar that completes an FTD day. The flag
is True on exactly one bar per confirmed attempt, so the cross
fires exactly once per FTD; a level condition would be wrong
here only in the sense of re-firing, and the cross form keeps
the entry rule in the house CROSS-based convention.

Short: never (long only -- there is no opposite in O'Neil's
FTD; a failed rally is an exit, not a short).

Exit long: on a later day's 23:00 bar, the completed day's
close (d_close) falls below the attempt_low that the FTD
confirmed. The held attempt_low is captured from the FTD
bar's ftd_attempt_low column and cleared once the exit fires,
so it fires once. The house 2xATR hard stop / 3xATR trail sit
behind this exit, with a 240-bar (10-day) max hold.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    ftd_flag = df["ftd_day"].fillna(False).astype(float)
    long_entry = crossed_above(ftd_flag, 0.5).fillna(False).to_numpy(bool)

    hour = pd.to_datetime(df["t"], unit="ms", utc=True).dt.hour.to_numpy(int)
    d_close = df["d_close"].to_numpy(float)
    ftd_low = df["ftd_attempt_low"].to_numpy(float)

    long_exit = np.zeros(n, dtype=bool)
    held = None  # attempt_low of the open long, from its FTD bar
    for i in range(n):
        if held is not None and hour[i] == 23 and d_close[i] < held:
            long_exit[i] = True
            held = None
        if held is None and long_entry[i]:
            low = ftd_low[i]
            held = float(low) if np.isfinite(low) else None
    df["long_entry"] = long_entry
    df["short_entry"] = np.zeros(n, dtype=bool)
    df["long_exit"] = long_exit
    df["short_exit"] = np.zeros(n, dtype=bool)
    return df
