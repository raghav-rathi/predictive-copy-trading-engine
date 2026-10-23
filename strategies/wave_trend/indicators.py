"""WaveTrend Oscillator indicators (LazyBear's canonical release).

    ap  = (h + l + c) / 3
    esa = EMA(ap, 10)
    d   = EMA(abs(ap - esa), 10)
    ci  = (ap - esa) / (0.015 * d)      # ci = 0 where d == 0 (zero-division guard)
    wt1 = EMA(ci, 21)                   # "tci" in the Pine source
    wt2 = SMA(wt1, 4)

Columns: ap, esa, d, ci, wt1, wt2 (+ atr for the risk layer).

No lookahead: every value at bar j uses data through bar j only
(rolling windows with min_periods=n, ewm with min_periods=n).
"""

import numpy as np
import pandas as pd

from strategies import base as B

N1 = 10       # esa / d EMA length (canonical)
N2 = 21       # ci EMA length (canonical)
WT2_LEN = 4   # wt1 SMA length (canonical)


def wavetrend(h: pd.Series, l: pd.Series, c: pd.Series,
              n1: int = N1, n2: int = N2, wt2_len: int = WT2_LEN) -> pd.DataFrame:
    """Compute the full WaveTrend chain from OHLC, bar j through bar j only."""
    ap = ((h + l + c) / 3.0).rename("ap")
    esa = B.ema(ap, n1).rename("esa")
    d = B.ema((ap - esa).abs(), n1).rename("d")
    raw_ci = (ap - esa) / (0.015 * d)
    # Guard: d == 0 means ap == esa for the whole window (perfectly flat
    # price) -> ci would be 0/0 = NaN. Flat price has zero momentum, so
    # the correct oscillator value is 0. (d NaN from warmup stays NaN.)
    ci = raw_ci.where(d.ne(0), 0.0).rename("ci")
    wt1 = B.ema(ci, n2).rename("wt1")
    wt2 = B.sma(wt1, wt2_len).rename("wt2")
    return pd.DataFrame(
        {"ap": ap, "esa": esa, "d": d, "ci": ci, "wt1": wt1, "wt2": wt2}
    )


def add_indicators(df: pd.DataFrame, n1: int = N1, n2: int = N2,
                   wt2_len: int = WT2_LEN) -> pd.DataFrame:
    df = df.copy()
    wt = wavetrend(df["h"], df["l"], df["c"], n1=n1, n2=n2, wt2_len=wt2_len)
    for col in wt.columns:
        df[col] = wt[col].to_numpy()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
