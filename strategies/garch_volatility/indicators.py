"""GARCH(1,1) volatility-regime indicators (Bollerslev, 1986).

Forecast variance recursion on 1h log returns r_t = ln(c_t / c_{t-1}):

    sigma2_t = omega + alpha * r_{t-1}^2 + beta * sigma2_{t-1}

with FIXED a priori params omega=1e-8, alpha=0.08, beta=0.90
(RiskMetrics-style; no MLE fitting, no PnL tuning). The recursion is
seeded at the unconditional variance omega / (1 - alpha - beta) =
1e-8 / 0.02 = 5e-7. sigma2_t uses only returns through bar t-1, so the
forecast vol on bar i is known from data through bar i-1's close.

Regime: forecast vol sigma_t = sqrt(sigma2_t) vs its trailing
1000-bar percentiles. NORMAL band = 30th-70th percentile. Trading
only inside the band avoids breakouts in panic (very high vol) and
dead (very low vol) regimes.

Columns:

    log_ret       -- 1h log return (first bar 0)
    garch_var     -- forecast variance sigma2_t
    garch_vol     -- forecast volatility sigma_t
    vol_p30       -- trailing 1000-bar 30th percentile of garch_vol
    vol_p70       -- trailing 1000-bar 70th percentile of garch_vol
    vol_normal    -- True when vol_p30 <= garch_vol <= vol_p70
    prev_high_20  -- highest high of the previous 20 bars (excl. current)
    prev_low_20   -- lowest low of the previous 20 bars (excl. current)
    atr           -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
(and the forecast vol itself only through bar i-1).
"""

import numpy as np
import pandas as pd

from strategies import base as B

OMEGA = 1e-8
ALPHA = 0.08
BETA = 0.90
PCT_N = 1000
RANGE_N = 20

INDICATOR_COLS = ["log_ret", "garch_var", "garch_vol", "vol_p30",
                  "vol_p70", "vol_normal", "prev_high_20", "prev_low_20",
                  "atr"]


def add_indicators(df: pd.DataFrame, omega: float = OMEGA,
                   alpha: float = ALPHA, beta: float = BETA,
                   pct_n: int = PCT_N,
                   range_n: int = RANGE_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    r = np.zeros(n)
    if n > 1:
        r[1:] = np.log(c[1:] / c[:-1])
    sigma2 = np.full(n, np.nan)
    if n:
        sigma2[0] = omega / (1.0 - alpha - beta)
        for i in range(1, n):
            sigma2[i] = omega + alpha * r[i - 1] ** 2 + beta * sigma2[i - 1]
    vol = np.sqrt(sigma2)
    vol_s = pd.Series(vol, index=df.index)
    p30 = vol_s.rolling(pct_n, min_periods=pct_n).quantile(0.30)
    p70 = vol_s.rolling(pct_n, min_periods=pct_n).quantile(0.70)
    df["log_ret"] = r
    df["garch_var"] = sigma2
    df["garch_vol"] = vol
    df["vol_p30"] = p30
    df["vol_p70"] = p70
    df["vol_normal"] = ((vol_s >= p30) & (vol_s <= p70)).fillna(False).astype(bool)
    df["prev_high_20"] = df["h"].rolling(range_n, min_periods=range_n).max().shift(1)
    df["prev_low_20"] = df["l"].rolling(range_n, min_periods=range_n).min().shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
