"""Original Turtle Rules -- Donchian channels + ATR(20) as N.

Richard Dennis / William Eckhardt's Turtle system (Curtis Faith, 2003),
adapted from daily to 1h bars: the original 20/55/10/20-day lookbacks
become 20/55/10/20-bar lookbacks. Columns:

    dc20_high / dc20_low       -- System-1 entry channel (20-bar Donchian)
    dc55_high / dc55_low       -- System-2 entry channel (55-bar Donchian)
    exit10_high / exit10_low   -- System-1 exit channel (10-bar Donchian)
    exit20_high / exit20_low   -- System-2 exit channel (20-bar Donchian)
    atr                        -- ATR(20), the Turtles' "N" (volatility unit)

No lookahead: every rolling window on bar j uses bars through j only.
The signals layer shifts the entry channels by 1 so a breakout bar's
close triggers the entry (the harness executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B

ENTRY_N = 20      # System-1 entry channel (shipped)
FAILSAFE_N = 55   # System-2 entry channel (shipped)
S1_EXIT_N = 10    # System-1 exit channel (shipped)
S2_EXIT_N = 20    # System-2 exit channel (shipped)
ATR_N = 20        # N


def add_indicators(
    df: pd.DataFrame,
    entry_n: int = ENTRY_N,
    failsafe_n: int = FAILSAFE_N,
    s1_exit_n: int = S1_EXIT_N,
    s2_exit_n: int = S2_EXIT_N,
) -> pd.DataFrame:
    """Donchian channels + ATR(20). Params are fixed at the shipped
    (20/55/10/20) values; the overrides exist only for the CALIBRATION.md
    S1-only sensitivity sweep."""
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]
    df["dc20_high"] = h.rolling(entry_n, min_periods=entry_n).max()
    df["dc20_low"] = l.rolling(entry_n, min_periods=entry_n).min()
    df["dc55_high"] = h.rolling(failsafe_n, min_periods=failsafe_n).max()
    df["dc55_low"] = l.rolling(failsafe_n, min_periods=failsafe_n).min()
    df["exit10_high"] = h.rolling(s1_exit_n, min_periods=s1_exit_n).max()
    df["exit10_low"] = l.rolling(s1_exit_n, min_periods=s1_exit_n).min()
    df["exit20_high"] = h.rolling(s2_exit_n, min_periods=s2_exit_n).max()
    df["exit20_low"] = l.rolling(s2_exit_n, min_periods=s2_exit_n).min()
    df["atr"] = B.atr(h, l, c, ATR_N)
    return df
