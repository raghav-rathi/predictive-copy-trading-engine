"""UTC-day session VWAP breakout indicators (causal, no lookahead).

VWAP is anchored to each UTC calendar day (reset 00:00 UTC):
    VWAP = cumulative sum(tp * v) / sum(v) since the session start,
    tp = (h + l + c) / 3.
The band is VWAP +/- 1.0 volume-weighted standard deviation of
typical price since the session start, computed from cumulative
sums (causal):
    Var = sum(v * tp^2) / sum(v) - VWAP^2,  SD = sqrt(max(Var, 0)).
The volume gate compares the bar's volume with the session's
average bar volume through bar i (inclusive):
    avg_vol = sum(v) / bars_in_session.

This is the same session-VWAP construction as the existing
vwap_bollinger_bands strategy, but with a 1.0-SD band and WITHOUT
its ADX(14) < 25 ranging-regime filter — the point of this build
is to test the raw VWAP breakout without the regime gate.

Degenerate-band guard: on the first bars of a session the SD is
computed from very few bars (exactly 0 on the first bar, since a
single point has no variance). Entries are therefore only
considered from the 3rd bar of a session onward
(session_bar >= 3, see signals.py); before that the band is not
a meaningful breakout level. This is a guard against a zero-width
band, not a parameter tuned on the backtest window.

Columns:
    vwap        -- session VWAP
    vwap_sd     -- volume-weighted SD of tp around VWAP since session start
    vwap_upper  -- VWAP + 1.0 * SD
    vwap_lower  -- VWAP - 1.0 * SD
    session_bar -- 1-based bar index within the UTC day
    session_avg_vol -- session average bar volume through bar i
    vol_above_avg -- bar volume above the session average
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's
close only (cumulative sums include bar i and exclude everything
after it).
"""

import numpy as np
import pandas as pd

from strategies import base as B

BAND_K = 1.0
MIN_SESSION_BARS = 3  # degenerate-band guard (see module docstring)

INDICATOR_COLS = ["vwap", "vwap_sd", "vwap_upper", "vwap_lower",
                  "session_bar", "session_avg_vol", "vol_above_avg", "atr"]


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
    session_bar = pd.Series(np.arange(len(df))).groupby(day).cumcount().to_numpy() + 1
    session_avg_vol = cum_v / session_bar
    df["vwap"] = vwap
    df["vwap_sd"] = sd
    df["vwap_upper"] = vwap + BAND_K * sd
    df["vwap_lower"] = vwap - BAND_K * sd
    df["session_bar"] = session_bar
    df["session_avg_vol"] = session_avg_vol
    df["vol_above_avg"] = (v > session_avg_vol).fillna(False).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
