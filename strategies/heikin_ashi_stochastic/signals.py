"""Heikin Ashi + Stochastic signals.

LONG when all three hold on bar i:
- HA bullish: ha_close > ha_open
- trend filter: ha_close > ha_ema50
- %K crosses above %D (k[i] > d[i] and k[i-1] <= d[i-1])
  while %K < 30 (cross out of oversold)

SHORT is the mirror: HA bearish (ha_close < ha_open),
ha_close < ha_ema50, %K crosses below %D while %K > 70.

Exits on the opposite cross: a long exits when %K crosses
below %D; a short exits when %K crosses above %D. No
oversold/overbought condition on the exit — the cross alone
is the momentum rollover.

State machine (one pass, like macd_rsi_divergence): entries
are transition-only — a signal fires only when flat (or on a
flip bar, where an exit and the opposite entry land on the
same bar). While a position is held, repeated cross bars do
NOT re-enter. All conditions read bar-i values at bar i;
signal columns are boolean, no NaN, no lookahead. Execution
is at bar i+1's open per the house convention.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    ha_o = df["ha_open"].to_numpy(dtype=float)
    ha_c = df["ha_close"].to_numpy(dtype=float)
    ema50 = df["ha_ema50"].to_numpy(dtype=float)
    k = df["stoch_k"].to_numpy(dtype=float)
    d = df["stoch_d"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    for i in range(n):
        cross_up = i > 0 and k[i] > d[i] and k[i - 1] <= d[i - 1]
        cross_down = i > 0 and k[i] < d[i] and k[i - 1] >= d[i - 1]
        ha_bull = ha_c[i] > ha_o[i]
        ha_bear = ha_c[i] < ha_o[i]
        above_ema = ha_c[i] > ema50[i]
        below_ema = ha_c[i] < ema50[i]
        if pos == "long":
            if cross_down:
                lx[i] = True
                pos = None
        elif pos == "short":
            if cross_up:
                sx[i] = True
                pos = None
        if pos is None:
            if ha_bull and above_ema and cross_up and k[i] < 30:
                le[i] = True
                pos = "long"
            elif ha_bear and below_ema and cross_down and k[i] > 70:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
