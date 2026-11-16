"""Fourier dominant-cycle trend engine.

Rolling FFT on detrended log-closes (Hann window, 128 bars). Each bar
reconstructs the signal from the top-3 dominant frequencies whose
period lies in 8-64 bars, and trades the reconstructed cycle's slope
through an SMA(50) trend filter:

    fft_cycle -- reconstructed cycle value (last point of the window)
    fft_slope -- fft_cycle diff (slope of the reconstructed cycle)
    sma50     -- SMA(close, 50) trend filter
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: the FFT on bar j uses log-closes through bar j only
(causal trailing window). numpy FFT only, no other spectral library.

Caveat: the FFT assumes stationary cycles; crypto cycles drift, so
expect regime decay -- the reconstructed cycle is a lagging, smoothed
view of the recent past, not a forecast of the next swing.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 128  # FFT window (bars)
TOP_K = 3  # dominant frequencies kept in the reconstruction
PERIOD_MIN = 8  # shortest cycle period kept (bars)
PERIOD_MAX = 64  # longest cycle period kept (bars)
SMA_N = 50  # trend-filter length


def _reconstruct_cycle(logc: np.ndarray, window: int = WINDOW,
                       top_k: int = TOP_K) -> np.ndarray:
    """Reconstructed cycle value per bar (NaN before the window fills).

    For each trailing ``window``-bar window: remove the linear trend,
    apply a Hann window, rFFT, keep only the top-``top_k`` magnitude
    bins whose period is in [8, 64] bars, inverse-transform, and take
    the last point.
    """
    n = len(logc)
    out = np.full(n, np.nan)
    hann = np.hanning(window)
    x = np.arange(window, dtype=float)
    freqs = np.fft.rfftfreq(window, d=1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        periods = np.where(freqs > 0, 1.0 / np.where(freqs > 0, freqs, np.nan), np.inf)
    keep = (periods >= PERIOD_MIN) & (periods <= PERIOD_MAX)
    keep_idx = np.where(keep)[0]
    for j in range(window - 1, n):
        w = logc[j - window + 1: j + 1]
        if not np.all(np.isfinite(w)):
            continue
        # linear detrend inside the window (no future data)
        a, b = np.polyfit(x, w, 1)
        detr = (w - (a * x + b)) * hann
        spec = np.fft.rfft(detr)
        mag = np.abs(spec)
        mag[~keep] = 0.0
        if not np.any(mag > 0):
            continue
        top = keep_idx[np.argsort(mag[keep_idx])[::-1][:top_k]]
        filt = np.zeros_like(spec)
        filt[top] = spec[top]
        recon = np.fft.irfft(filt, n=window)
        out[j] = recon[-1]
    return out


def add_indicators(df: pd.DataFrame, window: int = WINDOW,
                   top_k: int = TOP_K, sma_n: int = SMA_N) -> pd.DataFrame:
    df = df.copy()
    logc = np.log(df["c"].to_numpy(dtype=float))
    cyc = _reconstruct_cycle(logc, window=window, top_k=top_k)
    df["fft_cycle"] = cyc
    df["fft_slope"] = pd.Series(cyc, index=df.index).diff()
    df["sma50"] = B.sma(df["c"], sma_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
