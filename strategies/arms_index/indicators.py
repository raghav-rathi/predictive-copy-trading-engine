"""ARMS Index / TRIN (single-asset proxy).

The classic TRIN (Trading Index, Richard Arms) is an exchange-wide
breadth ratio: (advancing issues / declining issues) /
(advancing volume / declining volume). Values below 1 are bullish
(more volume flowing into advancers), above 1 bearish.

We have no exchange breadth feed on 1h crypto candles, so this is a
single-asset proxy: a bar counts as "up" when close > open and
"down" when close < open, tallied with their volumes over a rolling
10-bar window. That is a candle-count/volume proxy for TRIN, NOT
exchange-wide TRIN — see README.md.

    trin        -- (up_n / down_n) / (up_v / down_v), 10-bar window,
                   every component floored at 1 for the ratio
    trin_up_vol -- raw 10-bar up-volume sum (skip gate: 0 means no trade)
    trin_dn_vol -- raw 10-bar down-volume sum (skip gate: 0 means no trade)
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar j uses bars through j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 10  # shipped default: TRIN tally window (bars)


def add_indicators(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    df = df.copy()
    up = (df["c"] > df["o"]).astype(float)
    down = (df["c"] < df["o"]).astype(float)
    up_v = np.where(df["c"] > df["o"], df["v"], 0.0)
    down_v = np.where(df["c"] < df["o"], df["v"], 0.0)
    up_n = up.rolling(window, min_periods=window).sum().clip(lower=1.0)
    down_n = down.rolling(window, min_periods=window).sum().clip(lower=1.0)
    up_vol = pd.Series(up_v, index=df.index).rolling(
        window, min_periods=window).sum()
    down_vol = pd.Series(down_v, index=df.index).rolling(
        window, min_periods=window).sum()
    df["trin_up_vol"] = up_vol
    df["trin_dn_vol"] = down_vol
    # All four components floored at 1 so the ratio is always defined.
    df["trin"] = (up_n / down_n) / (
        up_vol.clip(lower=1.0) / down_vol.clip(lower=1.0))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
