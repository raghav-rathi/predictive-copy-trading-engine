"""Hurst exponent regime indicators.

Rolling Hurst exponent via rescaled-range (R/S) analysis on log
returns, window 200 bars, scales [10, 20, 40, 100]. For each scale
the 200-bar window is split into non-overlapping chunks; per chunk
R = max - min of the mean-adjusted cumulative deviation and
S = chunk standard deviation (ddof=1). Chunks with S == 0 (or
numerically zero, <= 1e-12) or R == 0 are skipped; the mean R/S
over the valid chunks is taken per scale, and H is the log-log
slope of mean R/S against scale (ordinary least squares). If
fewer than two scales yield a valid mean R/S, H = 0.5. H is
clipped to [0, 1].

Regime mode with hysteresis: the mode changes only after 3
consecutive bars in the same new band. Bands: H > 0.55 trend (+1),
H < 0.45 reversion (-1), 0.45-0.55 neutral (0, no entries). A
neutral bar breaks a pending streak toward the other mode, and
3 consecutive neutral bars move the mode to 0.

Columns:
    log_ret  -- log close-to-close returns (first bar 0.0)
    hurst    -- rolling R/S Hurst exponent (0.5 before the window fills)
    mode     -- +1 trend, -1 reversion, 0 neutral (hysteresis state)
    ema20 / ema50 -- exponential moving averages of close
    rsi14    -- Wilder RSI(14) of close
    atr      -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

HURST_WINDOW = 200
HURST_SCALES = [10, 20, 40, 100]
TREND_BAND = 0.55
REVERSION_BAND = 0.45
HYSTERESIS_BARS = 3
_EPS = 1e-12

INDICATOR_COLS = ["hurst", "mode", "ema20", "ema50", "rsi14", "atr"]


def _hurst_rs(window: np.ndarray, scales=HURST_SCALES) -> float:
    """R/S Hurst estimate for one returns window (length HURST_WINDOW)."""
    log_rs = []
    log_n = []
    for s in scales:
        n_chunks = len(window) // s
        if n_chunks < 1:
            continue
        chunks = window[: n_chunks * s].reshape(n_chunks, s)
        means = chunks.mean(axis=1, keepdims=True)
        cum = np.cumsum(chunks - means, axis=1)
        r = cum.max(axis=1) - cum.min(axis=1)
        sd = chunks.std(axis=1, ddof=1)
        valid = (sd > _EPS) & (r > _EPS) & np.isfinite(sd) & np.isfinite(r)
        if not valid.any():
            continue
        mean_rs = float(np.mean(r[valid] / sd[valid]))
        if mean_rs <= 0 or not np.isfinite(mean_rs):
            continue
        log_rs.append(np.log(mean_rs))
        log_n.append(np.log(s))
    if len(log_rs) < 2:
        return 0.5
    slope = np.polyfit(log_n, log_rs, 1)[0]
    return float(np.clip(slope, 0.0, 1.0))


def _regime_mode(hurst: np.ndarray) -> np.ndarray:
    """Hysteresis state machine: the mode changes only after 3
    consecutive bars in the same new band (trend +1 / reversion -1 /
    neutral 0). A bar in a third band restarts the pending count;
    a bar back in the current band clears it."""
    n = len(hurst)
    mode = np.zeros(n, dtype=int)
    cur = 0
    pending_band = 0
    pending = 0
    for i in range(n):
        h = hurst[i]
        if not np.isfinite(h):
            cand = 0
        elif h > TREND_BAND:
            cand = 1
        elif h < REVERSION_BAND:
            cand = -1
        else:
            cand = 0
        if cand == cur:
            pending = 0
            pending_band = cur
        elif cand == pending_band:
            pending += 1
            if pending >= HYSTERESIS_BARS:
                cur = cand
                pending = 0
                pending_band = cur
        else:
            pending_band = cand
            pending = 1
        mode[i] = cur
    return mode


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    log_ret = np.zeros(n)
    log_ret[1:] = np.log(c[1:] / c[:-1])
    log_ret[~np.isfinite(log_ret)] = 0.0
    df["log_ret"] = log_ret

    hurst = np.full(n, 0.5)
    for i in range(HURST_WINDOW - 1, n):
        hurst[i] = _hurst_rs(log_ret[i - HURST_WINDOW + 1 : i + 1])
    df["hurst"] = hurst
    df["mode"] = _regime_mode(hurst)

    df["ema20"] = B.ema(df["c"], 20)
    df["ema50"] = B.ema(df["c"], 50)
    df["rsi14"] = B.rsi(df["c"], 14)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
