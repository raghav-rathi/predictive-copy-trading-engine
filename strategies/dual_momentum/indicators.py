"""Dual Momentum indicators (Gary Antonacci, 2014).

Absolute momentum: the 240-bar log return of the coin's close.
240 hourly bars (~10 days) is the 1h adaptation of Antonacci's
12-month lookback (see CALIBRATION.md); a literal 12-bar lookback
on 1h bars would be noise.

    abs_mom = log(c_t / c_{t-240})

Relative momentum: the coin's 240-bar log return minus the
equal-weight basket's 240-bar log return. The basket return is the
mean of the three coins' 240-bar log returns, so it can only be
computed once all three coins are aligned on t; the runner
(run_backtest.py) computes ``basket_ret`` / ``rel_mom`` /
``basket_close`` / ``mom_rank`` and attaches them to each coin's
frame. ``add_indicators`` itself only computes the per-coin
``abs_mom`` (plus ATR for the risk layer).

Columns:

    abs_mom      -- 240-bar log return of this coin
    basket_ret   -- mean 240-bar log return across BTC/ETH/HYPE
                    (attached by the runner; NaN standalone)
    basket_close -- geometric mean of the three closes (attached
                    by the runner; informational only)
    rel_mom      -- abs_mom - basket_ret (attached by the runner)
    mom_rank     -- 1 = highest rel_mom ... 3 = lowest (runner)
    n_coins      -- number of coins ranked (runner; 3)
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MOM_N = 240

INDICATOR_COLS = ["abs_mom", "atr"]


def add_indicators(df: pd.DataFrame, n: int = MOM_N) -> pd.DataFrame:
    df = df.copy()
    df["abs_mom"] = np.log(df["c"] / df["c"].shift(n))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
