"""Coin/BTC relative-strength ratio-line breakout indicators.

The ratio line is R = coin close / BTC close, with BTC closes
aligned on the bar timestamp ``t``. Breakouts are measured
against the ratio's own prior 20-bar range (excluding the
current bar, so the breakout test is causal):

    ratio_high20 -- max ratio over the prior 20 bars
    ratio_low20  -- min ratio over the prior 20 bars
    ratio_sma20  -- 20-bar mean ratio (the exit reference)

Benchmark sourcing (in priority order):
  1. ``benchmark_df`` passed explicitly (columns t, c) -- this
     is the path the unit tests exercise, and the path a
     backtest driver should use when it already holds BTC
     candles.
  2. Otherwise the shipped BTC cache is read (read-only) from
     ``strategies/data.py``'s CACHE_DIR,
     ``data/candles/BTC_1h.csv``. This keeps the standard
     single-frame harness working: SPEC.add_indicators takes
     one frame and still gets a real BTC benchmark.
  3. If neither is available, ValueError -- there is deliberately
     NO fallback proxy (a coin-vs-its-own-SMA ratio is not a
     relative-strength line, and silently substituting one
     would mislabel the strategy).

For the BTC leg itself the ratio is 1 by construction, so its
prior range is flat and no breakout can ever fire: BTC is the
benchmark, not a traded leg (see BACKTEST.md).

Alignment: left-join on ``t``, then forward-fill the benchmark
close (causal: a missing BTC bar reuses the last known BTC
close). Bars before the first available BTC close keep NaN
ratio and produce no signal.
"""

import os

import pandas as pd

from strategies import base as B
from strategies.data import CACHE_DIR

RANGE_N = 20
BTC_CACHE = os.path.join(CACHE_DIR, "BTC_1h.csv")


def _benchmark_series(benchmark_df):
    if benchmark_df is not None:
        btc = benchmark_df[["t", "c"]].copy()
        btc.columns = ["t", "btc_close"]
        return btc.drop_duplicates(subset="t", keep="last")
    if not os.path.exists(BTC_CACHE):
        raise ValueError(
            "relative_strength_breakout needs BTC benchmark candles: "
            "pass benchmark_df or provide data/candles/BTC_1h.csv"
        )
    btc = pd.read_csv(BTC_CACHE, usecols=["t", "c"])
    btc.columns = ["t", "btc_close"]
    # the shipped cache can carry a few duplicated timestamps;
    # dedupe (last wins) so the left-join never multiplies rows
    return btc.drop_duplicates(subset="t", keep="last")


def add_indicators(df: pd.DataFrame, benchmark_df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = df.copy()
    btc = _benchmark_series(benchmark_df)
    merged = df[["t"]].merge(btc, on="t", how="left")
    btc_close = merged["btc_close"].ffill().to_numpy(dtype=float)
    df["btc_close"] = btc_close
    ratio = df["c"] / df["btc_close"]
    df["ratio"] = ratio
    prior = ratio.shift(1)
    df["ratio_high20"] = prior.rolling(RANGE_N, min_periods=RANGE_N).max()
    df["ratio_low20"] = prior.rolling(RANGE_N, min_periods=RANGE_N).min()
    df["ratio_sma20"] = ratio.rolling(RANGE_N, min_periods=RANGE_N).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
