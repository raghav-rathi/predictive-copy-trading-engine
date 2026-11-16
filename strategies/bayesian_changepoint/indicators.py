"""Bayesian online changepoint detection (Adams & MacKay 2007).

Posterior run-length over log-returns with a Gaussian likelihood,
Normal-Inverse-Gamma conjugate prior, and a constant hazard h=0.01
(mean run length 100 bars). Per bar the recursion is:

    pred[r]   -- Student-t predictive of x_t given the current run
                 of length r (sufficient stats mu/kappa/alpha/beta)
    growth    -- joint[r] * (1-h) * pred[r] shifts to run length r+1
    cp        -- sum(joint * h * prior-predictive) starts a new run
    p_change  -- posterior P(run length 0) after normalising
    post_mean -- posterior-weighted mean return over run lengths

Columns:

    bocd_p_change   -- P(changepoint at this bar), in [0, 1]
    bocd_post_mean  -- posterior-weighted post-change mean log-return
    bocd_run_length -- MAP run length (bars since the last changepoint)
    atr             -- Wilder ATR(14) for the risk layer

Prior (chosen for hourly log-returns, sd ~0.01): mu0=0, kappa0=5,
alpha0=1, beta0=1e-4, i.e. a prior predictive Student-t with 2 dof
and scale ~0.011. kappa0=5 (not 1) matters: with a very weak mean
prior the posterior keeps a ~1% atom at run length 0, whose
prior-predictive density explains a genuine mean shift almost as
well as a changepoint does, so P(change) peaks near 0.43 on an
8-sigma shift and the 0.5 detection threshold never fires. A
moderate kappa0 sharpens detection (P(change) ~0.9 on the same
shift) while still letting the post-change mean adapt within a few
bars.

Caveat: the detector also fires on volatility-only shifts, not just
mean shifts -- a volatility jump resets the run and the post-change
mean is then estimated from a handful of noisy bars, so the sign of
bocd_post_mean right after a changepoint is low-information.

No lookahead: every quantity on bar j uses log-returns through bar j
only. Pure numpy; no network.
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

HAZARD = 0.01  # constant hazard, mean run length 100 bars
RMAX = 200  # capped run length (performance)
MU0 = 0.0
KAPPA0 = 5.0
ALPHA0 = 1.0
BETA0 = 1e-4  # prior variance scale ~(0.01)^2 hourly returns
P_CHANGE_THRESHOLD = 0.5


def _student_t_logpdf(x: float, mu: np.ndarray, scale: np.ndarray,
                      df: np.ndarray, lgamma_term: np.ndarray) -> np.ndarray:
    """Vectorised Student-t log density (df/location/scale arrays)."""
    z = (x - mu) / scale
    return (lgamma_term - 0.5 * np.log(df * math.pi) - np.log(scale)
            - 0.5 * (df + 1.0) * np.log1p(z * z / df))


def bocd(logrets: np.ndarray, hazard: float = HAZARD,
         rmax: int = RMAX) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run BOCD over log-returns. Returns (p_change, post_mean, run_length)."""
    n = len(logrets)
    p_change = np.zeros(n)
    post_mean = np.zeros(n)
    run_length = np.zeros(n, dtype=int)
    if n == 0:
        return p_change, post_mean, run_length

    r = np.arange(rmax + 1, dtype=float)
    kappa = KAPPA0 + r
    alpha = ALPHA0 + 0.5 * r
    df = 2.0 * alpha
    lgamma_term = np.array([math.lgamma((d + 1) / 2) - math.lgamma(d / 2)
                            for d in df])
    # prior predictive (run length 0) constants
    df0 = 2.0 * ALPHA0
    lg0 = math.lgamma((df0 + 1) / 2) - math.lgamma(df0 / 2)
    scale0 = math.sqrt(BETA0 * (KAPPA0 + 1) / (ALPHA0 * KAPPA0))

    joint = np.zeros(rmax + 1)
    joint[0] = 1.0
    # sufficient stats per run length (only entries with joint mass > 0
    # are meaningful; the rest hold the prior and are never read)
    mu = np.full(rmax + 1, MU0)
    beta = np.full(rmax + 1, BETA0)

    for t in range(1, n):
        x = logrets[t]
        if not np.isfinite(x):
            continue
        scale = np.sqrt(beta * (kappa + 1.0) / (alpha * kappa))
        log_pred = _student_t_logpdf(x, mu, scale, df, lgamma_term)
        # cap log-density to avoid overflow in exp (densities are O(10))
        pred = np.exp(np.clip(log_pred, -700, 700))
        log_pred0 = (lg0 - 0.5 * math.log(df0 * math.pi) - math.log(scale0)
                     - 0.5 * (df0 + 1.0) * math.log1p(((x - MU0) / scale0) ** 2 / df0))
        pred0 = math.exp(max(min(log_pred0, 700.0), -700.0))

        new_joint = np.zeros(rmax + 1)
        new_joint[1:] = joint[:-1] * (1.0 - hazard) * pred[:-1]
        # run-length cap: mass growing past RMAX folds back into RMAX
        new_joint[rmax] += joint[rmax] * (1.0 - hazard) * pred[rmax]
        new_joint[0] = np.sum(joint * hazard) * pred0
        total = new_joint.sum()
        if total <= 0 or not np.isfinite(total):
            new_joint = np.zeros(rmax + 1)
            new_joint[0] = 1.0
            total = 1.0
        new_joint /= total

        # update sufficient stats: run length r+1 inherits run r's stats
        new_mu = np.empty(rmax + 1)
        new_beta = np.empty(rmax + 1)
        new_mu[0] = MU0
        new_beta[0] = BETA0
        kappa_old = kappa[:-1]
        kappa_new = kappa_old + 1.0
        new_mu[1:] = (kappa_old * mu[:-1] + x) / kappa_new
        new_beta[1:] = beta[:-1] + 0.5 * kappa_old * (x - mu[:-1]) ** 2 / kappa_new
        # Note: the mass folded into the RMAX cap keeps the growth-path
        # stats (run RMAX-1 -> RMAX); the one-observation difference
        # vs the folded run's own stats is negligible at 200 bars.

        joint, mu, beta = new_joint, new_mu, new_beta
        p_change[t] = joint[0]
        post_mean[t] = float(np.sum(joint * mu))
        run_length[t] = int(np.argmax(joint))
    return p_change, post_mean, run_length


def add_indicators(df: pd.DataFrame, hazard: float = HAZARD,
                   rmax: int = RMAX) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    logrets = np.zeros(len(c))
    logrets[1:] = np.log(c[1:] / c[:-1])
    p_change, post_mean, run_length = bocd(logrets, hazard=hazard, rmax=rmax)
    df["bocd_p_change"] = p_change
    df["bocd_post_mean"] = post_mean
    df["bocd_run_length"] = run_length
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
