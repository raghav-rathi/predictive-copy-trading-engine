"""VPIN toxicity indicators.

Bulk Volume Classification (Easley/de Prado/O'Hara) applied per 1h bar,
then volume-bucket VPIN:

* per-bar buy volume:  buyV = v*(c-l)/(h-l);  sellV = v - buyV.
  If h == l the bar carries no price information, so split 50/50.
* bucket size V(i) = trailing 50-bar mean volume, recomputed causally
  per bar (rolling mean shifted by 1, so only bars strictly before i).
* bars are accumulated into volume buckets: a bucket closes once its
  filled volume reaches V(i); a bar that would overflow a bucket is
  split proportionally across buckets and the remainder carries into
  the next bucket.
* VPIN(i) = mean over the last 50 completed buckets of
  |buyV - sellV| / bucket_volume.
* vpin_pctile(i) = rolling rank of VPIN(i) against the trailing 252
  VPIN values (shifted by 1, strictly causal): the fraction of past
  values <= the current one.

Everything is causal: indicator column at bar i uses only bars <= i
(bucket target / percentile windows use bars strictly before i where
stated).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

BUCKET_VOL_SPAN = 50  # trailing bars in the causal volume mean defining bucket size
N_BUCKETS = 50  # completed buckets averaged into VPIN
PCTILE_SPAN = 252  # trailing bars for the VPIN percentile rank
LOW_SPAN = 20  # panic-low lookback used by the signal module


def _bucket_series(v: np.ndarray, buy_v: np.ndarray, sell_v: np.ndarray, n: int):
    """Accumulate bar buy/sell volume into variable-size volume buckets.

    Returns (end_idx, imbalance) for each completed bucket; imbalance is
    |buy - sell| / filled_volume in [0, 1].
    """
    vol_mean = (
        pd.Series(v)
        .rolling(BUCKET_VOL_SPAN, min_periods=BUCKET_VOL_SPAN)
        .mean()
        .shift(1)
        .to_numpy()
    )
    first = np.flatnonzero(~np.isnan(vol_mean))
    if len(first) == 0:
        return np.array([], dtype=np.int64), np.array([])
    vol_mean[: first[0]] = vol_mean[first[0]]
    vol_mean = np.where(np.isfinite(vol_mean), vol_mean, vol_mean[first[0]])
    vol_mean[vol_mean <= 0] = 1e-12

    ends: list[int] = []
    imbs: list[float] = []
    cur_buy = 0.0
    cur_sell = 0.0
    for i in range(n):
        target = float(vol_mean[i])
        rb = float(buy_v[i])
        rs = float(sell_v[i])
        guard = 0
        while rb + rs > 1e-18 and guard < 10_000:
            guard += 1
            space = target - (cur_buy + cur_sell)
            if space <= 0:
                # target shrank below what is already filled: finalize it
                tot = cur_buy + cur_sell
                imbs.append(abs(cur_buy - cur_sell) / tot if tot > 0 else 0.0)
                ends.append(i)
                cur_buy = cur_sell = 0.0
                continue
            take = rb + rs
            if take <= space:
                cur_buy += rb
                cur_sell += rs
                rb = rs = 0.0
            else:
                frac = space / take
                cur_buy += rb * frac
                cur_sell += rs * frac
                tot = cur_buy + cur_sell
                imbs.append(abs(cur_buy - cur_sell) / tot if tot > 0 else 0.0)
                ends.append(i)
                cur_buy = cur_sell = 0.0
                rb *= 1.0 - frac
                rs *= 1.0 - frac
    return np.array(ends, dtype=np.int64), np.array(imbs)


def _vpin_from_buckets(ends: np.ndarray, imbs: np.ndarray, n: int) -> np.ndarray:
    """VPIN(i) = mean of the last N_BUCKETS completed buckets with end <= i."""
    vpin = np.full(n, np.nan)
    if len(ends) == 0:
        return vpin
    ps = np.concatenate([[0.0], np.cumsum(imbs)])
    for i in range(n):
        j = int(np.searchsorted(ends, i, side="right")) - 1
        if j >= N_BUCKETS - 1:
            vpin[i] = (ps[j + 1] - ps[j + 1 - N_BUCKETS]) / N_BUCKETS
    return vpin


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    o = df["o"].to_numpy(float)
    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    c = df["c"].to_numpy(float)
    v = df["v"].to_numpy(float)
    n = len(df)

    rng = h - l
    buy_frac = np.where(rng > 0, (c - l) / rng, 0.5)
    buy_v = v * np.clip(buy_frac, 0.0, 1.0)
    sell_v = v - buy_v

    ends, imbs = _bucket_series(v, buy_v, sell_v, n)
    vpin = _vpin_from_buckets(ends, imbs, n)

    vpin_s = pd.Series(vpin, index=df.index)
    pctile = (
        vpin_s.shift(1)
        .rolling(PCTILE_SPAN, min_periods=PCTILE_SPAN)
        .apply(lambda x: float((x <= x[-1]).mean()), raw=True)
    )

    close = df["c"]
    out["buy_v"] = buy_v
    out["sell_v"] = sell_v
    out["vpin"] = vpin
    out["vpin_pctile"] = pctile
    out["low_20"] = close.rolling(LOW_SPAN, min_periods=LOW_SPAN).min()
    out["high_20"] = close.rolling(LOW_SPAN, min_periods=LOW_SPAN).max()
    return out
