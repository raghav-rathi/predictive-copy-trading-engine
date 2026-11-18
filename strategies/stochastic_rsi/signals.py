"""StochRSI cross signals.

Long entry:  %K crosses above %D AND %K on the prior bar was < 20
             (cross rising out of oversold).
Short entry: %K crosses below %D AND %K on the prior bar was > 80.
Long exit:   %K crosses below %D OR %K crosses above 80.
Short exit:  %K crosses above %D OR %K crosses below 20.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). Crosses use strategies.base
crossed_above / crossed_below (strict cross of the current bar
vs the prior bar); the oversold/overbought gate reads %K on the
prior bar only (shift(1)), never the current bar.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stochrsi_k"]
    d = df["stochrsi_d"]
    k_prev = k.shift(1)
    cross_up = B.crossed_above(k, d).fillna(False)
    cross_dn = B.crossed_below(k, d).fillna(False)
    k_above_80 = B.crossed_above(k, 80).fillna(False)
    k_below_20 = B.crossed_below(k, 20).fillna(False)
    df["long_entry"] = (cross_up & (k_prev < 20).fillna(False)).astype(bool)
    df["short_entry"] = (cross_dn & (k_prev > 80).fillna(False)).astype(bool)
    df["long_exit"] = (cross_dn | k_above_80).astype(bool)
    df["short_exit"] = (cross_up | k_below_20).astype(bool)
    return df
