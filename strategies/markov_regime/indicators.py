"""Markov regime-switching indicators (Hamilton, 1989).

A 2-state Gaussian hidden Markov model on 1h log returns,
implemented from scratch with numpy (scaled forward-backward EM,
25 iterations, no external HMM library). The states are

    calm      -- low-volatility Gaussian
    turbulent -- high-volatility Gaussian

Calibration: the HMM is fit ONCE on the first 1000 log returns of
each coin (the in-sample calibration window, documented in
CALIBRATION.md). After fitting, the causal forward filter is run
over all bars with the fitted parameters, so the regime on bar i
uses only returns through bar i plus parameters fit on the first
1000 bars -- no lookahead beyond the documented calibration
window. The high-volatility state is whichever fitted state has
the larger sigma.

Columns:

    logret    -- log(c_t / c_{t-1})
    turb_prob -- forward-filtered P(turbulent | returns through t)
    regime    -- 1 = turbulent, 0 = calm (turb_prob > 0.5)
    ema_fast  -- EMA(12) of close
    ema_slow  -- EMA(26) of close
    rsi       -- Wilder RSI(14)
    atr       -- Wilder ATR(14) for the risk layer

EM initialisation is deterministic: returns are split at the
median absolute return into a low-|r| and a high-|r| group, and
each state's (mu, sigma) starts at its group's moments. The
transition matrix starts at [[0.95, 0.05], [0.05, 0.95]] and the
initial distribution at [0.5, 0.5]. Sigmas are floored at 1e-6 so
a degenerate (constant-return) window cannot divide by zero.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CAL_N = 1000
N_ITER = 25
EMA_FAST = 12
EMA_SLOW = 26
RSI_N = 14

INDICATOR_COLS = ["logret", "turb_prob", "regime", "ema_fast",
                  "ema_slow", "rsi", "atr"]


def _gauss_pdf(r, mu, sigma):
    return np.exp(-0.5 * np.log(2.0 * np.pi * sigma ** 2)
                  - (r - mu) ** 2 / (2.0 * sigma ** 2))


def _forward_backward(r, mu, sigma, A, pi):
    """Scaled forward-backward. Returns (gamma, xi, loglik)."""
    T = len(r)
    K = 2
    Bmat = np.column_stack([_gauss_pdf(r, mu[k], sigma[k])
                            for k in range(K)])
    alpha = np.zeros((T, K))
    c = np.zeros(T)
    alpha[0] = pi * Bmat[0]
    c[0] = alpha[0].sum()
    if c[0] <= 0:
        c[0] = 1.0
    alpha[0] /= c[0]
    for t in range(1, T):
        alpha[t] = (alpha[t - 1] @ A) * Bmat[t]
        c[t] = alpha[t].sum()
        if c[t] <= 0:
            c[t] = 1.0
        alpha[t] /= c[t]
    beta = np.zeros((T, K))
    beta[T - 1] = 1.0
    for t in range(T - 2, -1, -1):
        beta[t] = (A @ (Bmat[t + 1] * beta[t + 1])) / c[t + 1]
    gamma = alpha * beta
    gamma = gamma / gamma.sum(axis=1, keepdims=True).clip(min=1e-300)
    xi = np.zeros((T - 1, K, K))
    for t in range(T - 1):
        m = (alpha[t][:, None] * A
             * (Bmat[t + 1] * beta[t + 1])[None, :]) / c[t + 1]
        xi[t] = m / m.sum().clip(min=1e-300)
    loglik = float(np.log(c).sum())
    return gamma, xi, loglik


def _forward_filter(r, mu, sigma, A, pi):
    """Causal filtered posteriors alpha[t, k] = P(state k | r_..t)."""
    T = len(r)
    K = 2
    Bmat = np.column_stack([_gauss_pdf(r, mu[k], sigma[k])
                            for k in range(K)])
    alpha = np.zeros((T, K))
    alpha[0] = pi * Bmat[0]
    s = alpha[0].sum()
    alpha[0] /= s if s > 0 else 1.0
    for t in range(1, T):
        alpha[t] = (alpha[t - 1] @ A) * Bmat[t]
        s = alpha[t].sum()
        alpha[t] /= s if s > 0 else 1.0
    return alpha


def fit_hmm_2state(r, n_iter: int = N_ITER):
    """Fit a 2-state Gaussian HMM to a 1-D return array.

    Returns a dict with mu, sigma, A, pi, gamma (smoothed
    posterior on the fitted window) and loglik. Deterministic.
    """
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    T = len(r)
    if T < 10:
        return {"mu": np.array([0.0, 0.0]),
                "sigma": np.array([1e-3, 1e-3]),
                "A": np.array([[0.95, 0.05], [0.05, 0.95]]),
                "pi": np.array([0.5, 0.5]),
                "gamma": np.full((max(T, 1), 2), 0.5),
                "loglik": 0.0}
    # Deterministic init: split at the median absolute return.
    med = np.median(np.abs(r))
    low = np.abs(r) <= med
    high = ~low
    if low.sum() < 5 or high.sum() < 5:
        low = np.ones(T, dtype=bool)
        high = np.zeros(T, dtype=bool)
        high[T // 2:] = True
        low[T // 2:] = False
    mu = np.array([r[low].mean(), r[high].mean()])
    sigma = np.array([max(r[low].std(), 1e-6), max(r[high].std(), 1e-6)])
    A = np.array([[0.95, 0.05], [0.05, 0.95]])
    pi = np.array([0.5, 0.5])
    gamma = np.full((T, 2), 0.5)
    loglik = 0.0
    for _ in range(n_iter):
        gamma, xi, loglik = _forward_backward(r, mu, sigma, A, pi)
        pi = gamma[0] / gamma[0].sum()
        A = xi.sum(axis=0)
        A = A / A.sum(axis=1, keepdims=True).clip(min=1e-300)
        for k in range(2):
            w = gamma[:, k]
            denom = w.sum()
            if denom <= 0:
                continue
            mu[k] = float((w * r).sum() / denom)
            var = float((w * (r - mu[k]) ** 2).sum() / denom)
            sigma[k] = max(np.sqrt(var), 1e-6)
    return {"mu": mu, "sigma": sigma, "A": A, "pi": pi,
            "gamma": gamma, "loglik": loglik}


def add_indicators(df: pd.DataFrame, cal_n: int = CAL_N,
                   n_iter: int = N_ITER) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    logret = np.log(c / c.shift(1))
    df["logret"] = logret
    r_all = logret.to_numpy(dtype=float)
    idx = np.where(np.isfinite(r_all))[0]
    valid = r_all[idx]
    if len(valid) == 0:
        df["turb_prob"] = 0.5
        df["regime"] = 0
    else:
        fit = fit_hmm_2state(valid[:cal_n], n_iter=n_iter)
        high = int(np.argmax(fit["sigma"]))
        filt = _forward_filter(valid, fit["mu"], fit["sigma"],
                               fit["A"], fit["pi"])
        turb = np.full(len(df), np.nan)
        turb[idx] = filt[:, high]
        turb[0] = fit["pi"][high]
        turb = pd.Series(turb).ffill().fillna(0.5).to_numpy()
        df["turb_prob"] = turb
        df["regime"] = (turb > 0.5).astype(int)
    df["ema_fast"] = B.ema(c, EMA_FAST)
    df["ema_slow"] = B.ema(c, EMA_SLOW)
    df["rsi"] = B.rsi(c, RSI_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
