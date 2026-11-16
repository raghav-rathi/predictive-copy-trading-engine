"""Stridsman Volatility Quality Index (VQI).

FROZEN CONVENTION (several published variants exist; this is the one
implemented here, exactly as specified):

    e_t   = (close_t - close_{t-1}) / true_range_t   (per-bar efficiency)
    S_t   = sum of e over the trailing 10 bars
    VQI_t = WMA(S, 14)   (linearly weighted, most recent heaviest)

Rising VQI = "good" (directional) volatility: price is moving
efficiently in one direction relative to its range. Falling VQI =
"bad" (choppy) volatility: price is burning range without progress.

Columns:

    vqi_eff    -- e_t
    vqi_s      -- S_t (10-bar sum of e)
    vqi        -- VQI_t = WMA(S, 14)
    vqi_chg10  -- VQI_t - VQI_{t-10}
    vqi_gate   -- |vqi_chg10| >= 0.5 * median(|vqi_chg10|, 50)
    ema20      -- EMA(close, 20), the exit cross line
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every quantity on bar j uses OHLC through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EFF_N = 10  # bars summed into S_t
WMA_N = 14  # WMA length for VQI
CHG_N = 10  # VQI change lookback (bars)
GATE_MED_N = 50  # median lookback for the |change| gate
GATE_MULT = 0.5  # gate: |change| >= 0.5 * median(|change|, 50)
EMA_N = 20  # exit-cross EMA length


def wma(s: pd.Series, n: int) -> pd.Series:
    """Linearly weighted moving average (weight 1..n, newest heaviest)."""
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n, min_periods=n).apply(
        lambda x: float(np.dot(w, x)) / w.sum(), raw=True
    )


def add_indicators(df: pd.DataFrame, eff_n: int = EFF_N, wma_n: int = WMA_N,
                   chg_n: int = CHG_N, gate_med_n: int = GATE_MED_N,
                   gate_mult: float = GATE_MULT,
                   ema_n: int = EMA_N) -> pd.DataFrame:
    df = df.copy()
    tr = B.true_range(df["h"], df["l"], df["c"])
    dc = df["c"].diff()
    eff = (dc / tr.replace(0, np.nan)).fillna(0.0)
    df["vqi_eff"] = eff
    s = eff.rolling(eff_n, min_periods=eff_n).sum()
    df["vqi_s"] = s
    df["vqi"] = wma(s, wma_n)
    chg = df["vqi"].diff(chg_n)
    df["vqi_chg10"] = chg
    med = chg.abs().rolling(gate_med_n, min_periods=gate_med_n).median()
    df["vqi_gate"] = (chg.abs() >= gate_mult * med).fillna(False)
    df["ema20"] = B.ema(df["c"], ema_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
