"""Pairs-trading spread indicators (Gatev, Goetzmann & Rouwenhorst, 2006).

The spread is built from BTC vs ETH 1h closes. The hedge ratio
``beta`` is a rolling 500-bar OLS slope of log(BTC close) on
log(ETH close), recomputed every bar from the trailing 500 bars
only (fully causal):

    beta_t = Cov(log BTC, log ETH) / Var(log ETH)   over bars t-499..t
    spread_t = log(BTC_t) - beta_t * log(ETH_t)

``build_spread_frame`` assembles the synthetic spread instrument
the harness trades: USD spread OHLC (BTC o/h/l/c minus beta_t x
ETH o/h/l/c, with beta_t the trailing 500-bar beta at that bar),
volume = BTC volume, plus the ``beta`` and log-``spread`` columns.
``add_indicators`` then adds the rolling 100-bar mean/std of the
log-spread and the z-score, plus ATR(14) of the USD spread for
the risk layer:

    z_t = (spread_t - mean_100(spread)) / std_100(spread)

Columns on the spread frame:

    beta, spread   -- hedge ratio, log-spread
    spread_mean, spread_std, z
    atr            -- Wilder ATR(14) of the USD spread

No lookahead: beta, the spread and z on bar i use data through
bar i's close only. The first 499 bars have no beta (NaN) and the
first 598 bars have no z; warmup 600 covers both.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BETA_N = 500
Z_N = 100

INDICATOR_COLS = ["beta", "spread", "spread_mean", "spread_std", "z", "atr"]


def compute_beta(log_btc: pd.Series, log_eth: pd.Series,
                 n: int = BETA_N) -> pd.Series:
    """Rolling OLS slope of log_btc on log_eth over trailing n bars."""
    cov = log_btc.rolling(n, min_periods=n).cov(log_eth)
    var = log_eth.rolling(n, min_periods=n).var()
    return cov / var.replace(0, np.nan)


def build_spread_frame(btc: pd.DataFrame, eth: pd.DataFrame,
                       n: int = BETA_N) -> pd.DataFrame:
    """Assemble the synthetic BTC-ETH spread instrument (one book).

    ``btc`` / ``eth`` are window-filtered 1h OHLCV frames. They are
    inner-joined on t so every spread bar has both legs. The USD
    spread OHLC is BTC o/h/l/c minus beta_t x ETH o/h/l/c.
    """
    m = btc[["t", "o", "h", "l", "c", "v"]].merge(
        eth[["t", "o", "h", "l", "c"]],
        on="t", suffixes=("_btc", "_eth")).sort_values("t")
    m = m.reset_index(drop=True)
    log_btc = np.log(m["c_btc"])
    log_eth = np.log(m["c_eth"])
    beta = compute_beta(log_btc, log_eth, n)
    spread = log_btc - beta * log_eth
    out = pd.DataFrame({
        "t": m["t"],
        "o": m["o_btc"] - beta * m["o_eth"],
        "h": m["h_btc"] - beta * m["h_eth"],
        "l": m["l_btc"] - beta * m["l_eth"],
        "c": m["c_btc"] - beta * m["c_eth"],
        "v": m["v"],
        "beta": beta,
        "spread": spread,
    })
    return out


def add_indicators(df: pd.DataFrame, z_n: int = Z_N) -> pd.DataFrame:
    df = df.copy()
    mean = df["spread"].rolling(z_n, min_periods=z_n).mean()
    std = df["spread"].rolling(z_n, min_periods=z_n).std()
    df["spread_mean"] = mean
    df["spread_std"] = std
    df["z"] = (df["spread"] - mean) / std.replace(0, np.nan)
    df["z"] = df["z"].fillna(0.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
