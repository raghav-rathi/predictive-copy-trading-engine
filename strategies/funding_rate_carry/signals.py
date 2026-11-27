"""Funding-rate carry signals (directional, contrarian + carry).

The edge is twofold: a deeply one-sided 24h funding average
marks a crowded side (contrarian price mean-reversion), and
holding against the crowd harvests the funding payments
themselves (negative funding pays longs; positive funding
pays shorts).

    Long entry:  fund_avg_24h crosses BELOW -THRESH (funding
                 deeply negative: shorts pay longs).
    Short entry: fund_avg_24h crosses ABOVE +THRESH (funding
                 deeply positive: longs pay shorts).

    Long exit:   fund_avg_24h crosses ABOVE -THRESH/2
                 (funding normalized; or the opposite entry
                 fires).
    Short exit:  fund_avg_24h crosses BELOW +THRESH/2
                 (or the opposite entry fires).

THRESH = 0.0000125 (0.00125% per hour), set from the data
distribution BEFORE any backtest was run: the 90th
percentile of positive fund_avg_24h values pooled across
BTC/ETH/HYPE over the batch-48 window (see README.md /
CALIBRATION.md). The exit level is THRESH/2 = 0.00000625.

Entries are CROSS-based (crossed_above / crossed_below),
never level conditions, so a signal fires once per cross
instead of re-firing every bar the funding stays extreme.
Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
The house 2xATR hard stop / 3xATR trail sit behind these
exits, with a 168-bar max hold.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

# 90th percentile of positive fund_avg_24h, pooled across
# BTC/ETH/HYPE over the batch-48 window (computed from the
# local funding cache before any PnL was seen). The
# negative-side 90th percentile of |fund_avg_24h| is
# 0.00001252, essentially identical, so the symmetric
# threshold is consistent with the data on both sides.
THRESH = 0.0000125


def add_signals(df: pd.DataFrame, thresh: float = THRESH) -> pd.DataFrame:
    df = df.copy()
    avg = df["fund_avg_24h"]

    long_entry = crossed_below(avg, -thresh).fillna(False).to_numpy(bool)
    short_entry = crossed_above(avg, thresh).fillna(False).to_numpy(bool)
    # Opposite entry also exits (evaluated from the entry arrays
    # just built, so no ordering hazard).
    long_exit = (
        crossed_above(avg, -thresh / 2) | pd.Series(short_entry, index=df.index)
    ).fillna(False).to_numpy(bool)
    short_exit = (
        crossed_below(avg, thresh / 2) | pd.Series(long_entry, index=df.index)
    ).fillna(False).to_numpy(bool)

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
