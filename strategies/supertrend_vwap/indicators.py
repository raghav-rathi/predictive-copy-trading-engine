"""Supertrend + session VWAP agreement indicators.

Supertrend(10, 3.0) via base.supertrend (Olivier Seban; ATR
bands around the bar midpoint with a one-way ratchet; the
standard defaults are ATR 10 and multiplier 3). Session VWAP
anchored at 00:00 UTC via base.anchored_vwap: typical price
(h + l + c) / 3 volume-weighted, resetting each UTC day —
the same UTC-day anchor as vwap_session_breakout.

Columns:
    supertrend, supertrend_dir -- line and direction (+1 up / -1 down)
    vwap                       -- UTC-day session VWAP
    atr14                      -- ATR(14), diagnostic

No lookahead: every value on bar i uses data through bar i's
close only (the Supertrend ratchet and the VWAP cumulative
sums include bar i and exclude everything after it).
"""

import pandas as pd

from strategies import base as B

ST_N = 10
ST_K = 3.0


def add_indicators(
    df: pd.DataFrame,
    st_n: int = ST_N,
    st_k: float = ST_K,
) -> pd.DataFrame:
    df = df.copy()
    st = B.supertrend(df["h"], df["l"], df["c"], st_n, st_k)
    df["supertrend"] = st["supertrend"]
    df["supertrend_dir"] = st["supertrend_dir"]
    df["vwap"] = B.anchored_vwap(df["h"], df["l"], df["c"], df["v"], df["t"])
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
