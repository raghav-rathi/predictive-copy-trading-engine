"""UT Bot Alerts indicators (QuantNomad, TradingView; original idea HPotter).

ATR trailing stop, Heikin Ashi OFF (raw closes):

    xATR  = ATR(10) (Wilder)
    nLoss = KeyValue * xATR, KeyValue = 1.0 shipped

Trailing stop recursion, per bar (explicit loop). prev is the
previous bar's stop (0 if none):

    if close > prev and close[1] > prev: stop = max(prev, close - nLoss)
    elif close < prev and close[1] < prev: stop = min(prev, close + nLoss)
    elif close > prev: stop = close - nLoss
    else: stop = close + nLoss

The stop only ever ratchets in the direction of the prevailing
trend: in an uptrend it trails below price (never moves down),
in a downtrend it trails above price (never moves up). A flip
of the stop from one side of price to the other is the trend
change the signals trade.

Columns:
    xatr    -- ATR(10)
    nloss   -- KeyValue * xATR
    ut_stop -- trailing stop

No lookahead: the value on bar j uses data through bar j's close
only (Wilder ATR is causal; the recursion reads only the previous
bar's stop and close).
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 10       # shipped default
KEY_VALUE = 1.0  # shipped default


def add_indicators(
    df: pd.DataFrame,
    key_value: float = KEY_VALUE,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    df["xatr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    df["nloss"] = key_value * df["xatr"]

    c_v = df["c"].to_numpy(dtype=float)
    nl_v = df["nloss"].to_numpy(dtype=float)
    m = len(df)
    stop = np.full(m, np.nan)
    for i in range(m):
        if not np.isfinite(nl_v[i]) or not np.isfinite(c_v[i]):
            continue
        prev = stop[i - 1] if i > 0 and np.isfinite(stop[i - 1]) else 0.0
        if i == 0:
            stop[i] = c_v[i] - nl_v[i]
        elif c_v[i] > prev and c_v[i - 1] > prev:
            stop[i] = max(prev, c_v[i] - nl_v[i])
        elif c_v[i] < prev and c_v[i - 1] < prev:
            stop[i] = min(prev, c_v[i] + nl_v[i])
        elif c_v[i] > prev:
            stop[i] = c_v[i] - nl_v[i]
        else:
            stop[i] = c_v[i] + nl_v[i]
    df["ut_stop"] = stop
    return df
