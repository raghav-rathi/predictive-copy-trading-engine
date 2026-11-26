"""Dynamic Momentum Index (DMI) indicators.

Tushar Chande & Stanley Kroll, "The New Technical Trader"
(1994); Stocks & Commodities V.11:5 "Stochastic RSI and
Dynamic Momentum Index". Chande's published formula:

    sd5    = stdev(close, 5)
    sd_avg = SMA(sd5, 10)
    Vi     = sd5 / sd_avg
    TD     = clamp(int(14 / Vi), 5, 30)
    DMI    = RSI over the last TD price changes

The RSI here is the *definitional* form: RS from the simple
means of gains and losses over the last TD changes — NOT
Wilder smoothing. That is a deliberate choice: Chande's
original DMI uses a simple average over the variable window,
and Wilder smoothing over a changing window has no canonical
definition. (base.rsi is Wilder-smoothed and is NOT used
here.)

TD is a per-bar variable lookback: volatile bars shorten the
RSI window toward 5, quiet bars lengthen it toward 30.

Columns:
    sd5               -- rolling stdev(close, 5), pandas ddof=1
    sd_avg            -- SMA(sd5, 10)
    volatility_index  -- Vi = sd5 / sd_avg
    td                -- variable RSI lookback, clamped [5, 30]
    dmi               -- Dynamic Momentum Index, 0..100
    atr14             -- ATR(14), diagnostic

Edge cases: where sd5 and sd_avg are both 0 (a perfectly flat
stretch) Vi is undefined and DMI is NaN — no volatility, no
momentum reading. Where the TD window has only gains DMI is
100, only losses 0, and neither (all changes zero) 50. DMI is
NaN until sd_avg is defined (bar 13); WARMUP = 40 covers the
spin-up. No lookahead: every input is causal; TD at bar i
uses only closes through bar i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SD_N = 5
SD_AVG_N = 10
BASE_PERIOD = 14
TD_MIN = 5
TD_MAX = 30


def _dmi_values(
    close: pd.Series,
    base_period: int = BASE_PERIOD,
    sd_n: int = SD_N,
    sd_avg_n: int = SD_AVG_N,
    td_min: int = TD_MIN,
    td_max: int = TD_MAX,
):
    """Return (sd5, sd_avg, vi, td, dmi) series for ``close``."""
    sd5 = close.rolling(sd_n, min_periods=sd_n).std()
    sd_avg = sd5.rolling(sd_avg_n, min_periods=sd_avg_n).mean()
    vi = sd5 / sd_avg
    td_raw = (base_period / vi).where(vi > 0)
    td = td_raw.clip(lower=td_min, upper=td_max)
    td_v = np.floor(td.to_numpy(dtype=float))

    d = close.diff().to_numpy(dtype=float)
    n = len(close)
    dmi = np.full(n, np.nan)
    for i in range(n):
        tdi = td_v[i]
        if np.isnan(tdi):
            continue
        k = int(tdi)
        if i - k + 1 < 1:  # need k defined diffs; diffs start at index 1
            continue
        window = d[i - k + 1:i + 1]
        ag = float(np.clip(window, 0, None).mean())
        al = float((-np.clip(window, None, 0)).mean())
        if al == 0.0 and ag == 0.0:
            dmi[i] = 50.0
        elif al == 0.0:
            dmi[i] = 100.0
        elif ag == 0.0:
            dmi[i] = 0.0
        else:
            dmi[i] = 100.0 - 100.0 / (1.0 + ag / al)
    return sd5, sd_avg, vi, pd.Series(td_v, index=close.index), pd.Series(dmi, index=close.index)


def add_indicators(
    df: pd.DataFrame,
    base_period: int = BASE_PERIOD,
    sd_n: int = SD_N,
    sd_avg_n: int = SD_AVG_N,
    td_min: int = TD_MIN,
    td_max: int = TD_MAX,
) -> pd.DataFrame:
    df = df.copy()
    sd5, sd_avg, vi, td, dmi = _dmi_values(
        df["c"], base_period, sd_n, sd_avg_n, td_min, td_max
    )
    df["sd5"] = sd5
    df["sd_avg"] = sd_avg
    df["volatility_index"] = vi
    df["td"] = td
    df["dmi"] = dmi
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
