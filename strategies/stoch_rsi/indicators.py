"""Stochastic RSI indicators (Chande & Kroll).

Stochastic RSI applies the stochastic formula to the RSI itself
instead of price, so it oscillates on a 0..100 scale that reacts
faster to momentum extremes than raw RSI:

    rsi   = Wilder RSI(rsi_n) of close
    raw   = 100 * (rsi - min(rsi, stoch_n)) / (max(rsi, stoch_n) - min(rsi, stoch_n))
    k     = SMA(raw, k_n)        -- the fast "%K" line
    d     = SMA(k, d_n)          -- the slow "%D" line

The 0/0 case (RSI exactly constant over the stoch window) is guarded
without inventing a level: a dead-flat market pins raw to 50
(neutral), while a one-directional run — RSI pinned at its floor or
ceiling because every bar moved the same way — pins to the
informative extreme (0 when pinned low, 100 when pinned high). On
real noisy data the window is never exactly constant, so the guard
only ever fires on pathological or dead markets.

Columns:
    rsi      -- Wilder RSI(rsi_n)
    stoch_k  -- SMA(3) of the stochastic RSI (the trigger line)
    stoch_d  -- SMA(3) of stoch_k (the smoothing line)

No lookahead: the value on bar j uses data through bar j's close
only (rolling windows with min_periods=n, Wilder EWM for RSI).
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 14       # shipped default
STOCH_N = 14     # shipped default
K_N = 3          # shipped default
D_N = 3          # shipped default


def stochastic_rsi(
    c: pd.Series,
    rsi_n: int = RSI_N,
    stoch_n: int = STOCH_N,
    k_n: int = K_N,
    d_n: int = D_N,
) -> pd.DataFrame:
    """Stochastic RSI %K/%D lines for a close series."""
    rsi = B.rsi(c, rsi_n)
    rsi_min = rsi.rolling(stoch_n, min_periods=stoch_n).min()
    rsi_max = rsi.rolling(stoch_n, min_periods=stoch_n).max()
    span = rsi_max - rsi_min
    ratio = 100.0 * (rsi - rsi_min) / span  # NaN when span is 0 or not yet formed
    # guard the 0/0 case (RSI constant over the window): dead-flat
    # market -> 50 (neutral); one-directional run with RSI pinned at
    # its floor/ceiling -> the informative extreme. Warmup NaNs stay NaN.
    flat = (span == 0) & span.notna()
    c_range = c.rolling(stoch_n, min_periods=stoch_n).max() - c.rolling(
        stoch_n, min_periods=stoch_n
    ).min()
    dead = flat & (c_range == 0)
    pin = np.where(np.asarray(rsi) >= 50.0, 100.0, 0.0)
    raw = pd.Series(
        np.where(dead, 50.0, np.where(flat, pin, np.asarray(ratio))),
        index=c.index,
    ).clip(0.0, 100.0)
    k = B.sma(raw, k_n)
    d = B.sma(k, d_n)
    return pd.DataFrame({"rsi": rsi, "stoch_raw": raw, "stoch_k": k, "stoch_d": d})


def add_indicators(
    df: pd.DataFrame,
    rsi_n: int = RSI_N,
    stoch_n: int = STOCH_N,
    k_n: int = K_N,
    d_n: int = D_N,
) -> pd.DataFrame:
    df = df.copy()
    sr = stochastic_rsi(df["c"], rsi_n, stoch_n, k_n, d_n)
    df["rsi"] = sr["rsi"]
    df["stoch_raw"] = sr["stoch_raw"]
    df["stoch_k"] = sr["stoch_k"]
    df["stoch_d"] = sr["stoch_d"]
    return df
