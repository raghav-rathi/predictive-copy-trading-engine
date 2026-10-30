"""Order-flow imbalance indicators (causal, no lookahead).

Bar-delta proxy of footprint delta. True footprint delta
needs tick-level bid/ask classification (aggressive buys
minus aggressive sells); 1h OHLCV bars carry no bid/ask
split, so the per-bar signed volume is proxied from the
bar's own price travel:

    delta[i] = v[i] * (c[i] - o[i]) / max(h[i] - l[i], eps),
    clipped to [-v[i], v[i]]

A bar that closes at its high scores +v (all volume read as
buying pressure); a bar closing at its low scores -v; a doji
scores 0. This is a proxy, not measured order flow, and is
labelled as such everywhere it is reported.

    imbalance[i] = sum(delta[i-4..i]) / sum(v[i-4..i]),
    in [-1, 1] by construction (rolling 5-bar window).

Columns:
    bar_delta, imbalance, ema20, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 5
EMA_N = 20
EPS = 1e-12


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = np.maximum(df["h"].to_numpy(dtype=float) - df["l"].to_numpy(dtype=float), EPS)
    v = df["v"].to_numpy(dtype=float)
    raw = v * (df["c"].to_numpy(dtype=float) - df["o"].to_numpy(dtype=float)) / rng
    delta = np.clip(raw, -v, v)
    df["bar_delta"] = delta
    d = pd.Series(delta)
    vol = pd.Series(v)
    imb = d.rolling(WINDOW, min_periods=WINDOW).sum() / vol.rolling(WINDOW, min_periods=WINDOW).sum().replace(0, np.nan)
    df["imbalance"] = imb.clip(-1.0, 1.0)
    df["ema20"] = B.ema(df["c"], EMA_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
