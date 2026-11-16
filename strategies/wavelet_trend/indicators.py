"""Wavelet-trend engine: DWT (db4, level 3) approximation slope.

PyWavelets is NOT installed, so the db4 DWT is implemented here in
pure numpy as a filter-bank transform with half-point symmetric
extension (the ``symmetric`` boundary mode of PyWavelets' wavedec).
The 8-tap Daubechies-4 low-pass decomposition filter (Daubechies
1992, "Ten Lectures on Wavelets", Table 6.1; also Wikipedia
"Daubechies wavelet") is hardcoded below; its taps sum to sqrt(2):

    h = [0.2303778133088964, 0.7148465705529154, 0.6308807679298589,
         -0.0279837694168599, -0.1870348117190931, 0.0308413818355607,
         0.0328830116668852, -0.0105974017850690]

and the high-pass filter is the quadrature mirror
g[k] = (-1)^k * h[7-k]. One level: extend by 7 samples each side
(mirror without repeating the edge sample), correlate with h / g,
downsample by 2 (even indices). Synthesis upsamples (zeros at odd
positions), convolves with the same h / g, and trims 7 samples off
the front. With all detail coefficients kept, reconstruction is
exact to ~1e-15 (verified in the tests); the approximation-only
reconstruction zeroes the details at all three levels.

Columns:

    wav_approx -- level-3 approximation-only reconstruction (denoised
                  trend); details at all three levels are zeroed
    wav_slope  -- wav_approx diff over a 5-bar window
    atr        -- Wilder ATR(14) for the risk layer

Causality / boundary effects: the approximation at bar j is computed
from the trailing 64 closes only (a sliding window ending at j), so
no future data is used. The symmetric extension mirrors the window's
own past at both edges, so there is no wrap-around discontinuity
(a periodic extension would pull the last value toward the
window-start price -- on a 0-to-10 linear ramp that error reaches
~5.7, vs ~0.26 here). The remaining boundary effect is a small edge
bias: on a clean linear ramp the approximation's last value sits
~0.17 below the true end value, and the interior (8 bars in) is
accurate to ~0.07. The slope (a difference of two approximations
from overlapping windows) cancels most of that bias.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 64  # trailing window for the DWT (bars)
LEVELS = 3  # DWT levels
SLOPE_N = 5  # slope window (bars)

# Daubechies-4 low-pass decomposition filter (8 taps), sum == sqrt(2).
DB4_H = np.array([
    0.2303778133088964, 0.7148465705529154, 0.6308807679298589,
    -0.0279837694168599, -0.1870348117190931, 0.0308413818355607,
    0.0328830116668852, -0.0105974017850690,
])
# Quadrature-mirror high-pass decomposition filter.
DB4_G = np.array([((-1) ** k) * DB4_H[7 - k] for k in range(8)])

_PAD = len(DB4_H) - 1  # 7


def _extend(x: np.ndarray) -> np.ndarray:
    """Half-point symmetric extension (mirror, edge sample not repeated)."""
    return np.concatenate([x[_PAD:0:-1], x, x[-2:-_PAD - 2:-1]])


def _dwt_level(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """One DWT level: (approx coeffs, detail coeffs)."""
    xe = _extend(x)
    a = np.correlate(xe, DB4_H, mode="valid")[0::2]
    d = np.correlate(xe, DB4_G, mode="valid")[0::2]
    return a, d


def _idwt_level(a: np.ndarray, d: np.ndarray, n: int) -> np.ndarray:
    """One inverse DWT level, reconstructing ``n`` samples."""
    au = np.zeros(2 * len(a))
    au[::2] = a
    du = np.zeros(2 * len(d))
    du[::2] = d
    y = np.convolve(au, DB4_H) + np.convolve(du, DB4_G)
    return y[_PAD:_PAD + n]


def _wavedec(x: np.ndarray, levels: int = LEVELS):
    """3-level DWT. Returns (approx coeffs, [detail per level], sizes).

    sizes[k] is the signal length before level k (sizes[0] == len(x)).
    """
    a = np.asarray(x, dtype=float)
    ds: list[np.ndarray] = []
    sizes = [len(a)]
    for _ in range(levels):
        a, d = _dwt_level(a)
        ds.append(d)
        sizes.append(len(a))
    return a, ds, sizes


def _waverec(a: np.ndarray, ds: list[np.ndarray],
             sizes: list[int]) -> np.ndarray:
    """Inverse DWT from approx coeffs ``a`` and per-level details."""
    for k in range(len(ds) - 1, -1, -1):
        a = _idwt_level(a, ds[k], sizes[k])
    return a


def dwt_approx(x: np.ndarray, levels: int = LEVELS) -> np.ndarray:
    """Approximation-only reconstruction of ``x`` (details zeroed)."""
    a, ds, sizes = _wavedec(x, levels)
    return _waverec(a, [np.zeros_like(d) for d in ds], sizes)


def build_transform_matrices(window: int = WINDOW,
                             levels: int = LEVELS):
    """(T, Tinv, n_approx, coeff_len) for a fixed window length.

    T maps a window to its coefficient vector [a_L, d_L, ..., d_1]
    (length > window: symmetric extension makes the transform
    redundant/overcomplete). Tinv is its left inverse, built by
    applying the inverse DWT to each coefficient basis vector, so
    Tinv @ T == I to machine precision. Approximation = Tinv @
    mask(T @ x) with the detail coefficients zeroed.
    """
    n_approx_holder: list[int] = []

    def coeffs_of(v: np.ndarray) -> np.ndarray:
        a, ds, _ = _wavedec(v, levels)
        n_approx_holder.append(len(a))
        return np.concatenate([a] + list(reversed(ds)))

    eye = np.eye(window)
    cols = [coeffs_of(eye[i]) for i in range(window)]
    transform = np.column_stack(cols)
    coeff_len = transform.shape[0]
    n_approx = len(_wavedec(np.zeros(window), levels)[0])

    # inverse: coefficient basis vectors -> reconstructed signal
    # coefficient order is [a_L, d_L, d_{L-1}, ..., d_1]; recover the
    # per-level detail lengths by decomposing a dummy signal.
    _, ds_dummy, sizes = _wavedec(np.zeros(window), levels)
    detail_lens = [len(d) for d in reversed(ds_dummy)]

    def recon_of(c: np.ndarray) -> np.ndarray:
        a = c[:n_approx]
        ds: list[np.ndarray] = []
        off = n_approx
        for ln in detail_lens:  # d_L ... d_1 order
            ds.append(c[off:off + ln])
            off += ln
        ds = list(reversed(ds))  # back to per-level [d_1 ... d_L]
        return _waverec(a, ds, sizes)

    tinv = np.column_stack([recon_of(np.eye(coeff_len)[i])
                            for i in range(coeff_len)])
    return transform, tinv, n_approx, coeff_len


def add_indicators(df: pd.DataFrame, window: int = WINDOW,
                   levels: int = LEVELS, slope_n: int = SLOPE_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(c)
    approx = np.full(n, np.nan)
    if n >= window:
        transform, tinv, n_approx, _ = build_transform_matrices(window, levels)
        wins = np.lib.stride_tricks.sliding_window_view(c, window)
        coeffs = wins @ transform.T
        coeffs[:, n_approx:] = 0.0
        recon = coeffs @ tinv.T
        approx[window - 1:] = recon[:, -1]
    df["wav_approx"] = approx
    df["wav_slope"] = pd.Series(approx, index=df.index).diff(slope_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
