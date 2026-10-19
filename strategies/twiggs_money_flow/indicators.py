"""Twiggs Money Flow indicators.

Twiggs Money Flow replaces the Chaikin Money Flow's fixed-period
(h-l) denominator with the *true range*, so gap days don't distort the
money-flow ratio:

    trange_i = max(h_i - l_i, |h_i - c_{i-1}|, |l_i - c_{i-1}|)
    mf_i     = v_i * (2*c_i - h_i - l_i) / trange_i      (0 when trange_i = 0)
    TMF      = WilderEMA(mf, 21) / WilderEMA(v, 21)

No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

TMF_PERIOD = 21


def _wilder(s: pd.Series, n: int) -> pd.Series:
    """Wilder EMA, same form as strategies.base.atr."""
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def add_indicators(df: pd.DataFrame, period: int = TMF_PERIOD) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    trange = B.true_range(h, l, c)
    df["tmf_trange"] = trange
    close_pos = 2 * c - h - l
    # guard divide-by-zero: no true range (flat bar after flat close) => no money flow
    tr_np = trange.to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        mf_raw = v.to_numpy() * close_pos.to_numpy() / tr_np
    mf = pd.Series(np.where(tr_np > 0, mf_raw, 0.0), index=df.index)
    df["tmf_mf"] = mf
    mf_w = _wilder(mf, period)
    v_w = _wilder(v, period)
    tmf = mf_w / v_w.replace(0, np.nan)
    df["tmf"] = tmf
    df["atr"] = B.atr(h, l, c, 14)
    return df
