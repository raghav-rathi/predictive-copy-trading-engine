"""Session-anchored VWAP Bollinger Bands indicators.

VWAP is anchored to each UTC calendar day (reset 00:00 UTC):
    VWAP = cumulative sum(tp * v) / sum(v) since the session start,
    tp = (h + l + c) / 3.
The bands are VWAP +/- 2.0 volume-weighted standard deviations, where
the SD is the volume-weighted std of (tp - VWAP) since the session
start, computed from cumulative sums (causal):
    Var = sum(v * tp^2) / sum(v) - VWAP^2,  SD = sqrt(max(Var, 0)).
The regime filter is Wilder ADX(14).

Honest caveat: crypto trades 24/7, so there is no true session open
or overnight gap — the UTC-day anchor is an adaptation, not a market
open. Early in each UTC day the bands are computed from very few bars
and are correspondingly tight/noisy.

Columns:
    vwap       -- session VWAP
    vwap_sd    -- volume-weighted SD of tp around VWAP since session start
    vwap_upper -- VWAP + 2.0 * SD
    vwap_lower -- VWAP - 2.0 * SD
    adx        -- Wilder ADX(14)
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only (cumulative sums include bar i and exclude everything after it).
"""

import numpy as np
import pandas as pd

from strategies import base as B

BAND_K = 2.0
ADX_PERIOD = 14

INDICATOR_COLS = ["vwap", "vwap_sd", "vwap_upper", "vwap_lower", "adx", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    v = df["v"]
    day = pd.Series(
        pd.to_datetime(df["t"], unit="ms", utc=True)
    ).dt.floor("D").to_numpy()
    cum_pv = (tp * v).groupby(day).cumsum()
    cum_v = v.groupby(day).cumsum()
    cum_pv2 = (v * tp ** 2).groupby(day).cumsum()
    cum_v_safe = cum_v.replace(0, np.nan)
    vwap = cum_pv / cum_v_safe
    var = cum_pv2 / cum_v_safe - vwap ** 2
    sd = np.sqrt(var.clip(lower=0))
    df["vwap"] = vwap
    df["vwap_sd"] = sd
    df["vwap_upper"] = vwap + BAND_K * sd
    df["vwap_lower"] = vwap - BAND_K * sd
    df["adx"] = B.adx(df["h"], df["l"], df["c"], ADX_PERIOD)["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
