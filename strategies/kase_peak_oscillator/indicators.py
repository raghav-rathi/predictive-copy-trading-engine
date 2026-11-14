"""Kase Peak Oscillator -- Cynthia Kase, "Trading with the Odds" (1996).

Per the brief (Kase's published definitions):

    r(n)       = ln(C / C[1]) log returns
    sigma_n    = stddev of r over n bars
    KSDI_up(n) = ln(H / min(L, n)) / sigma_n
    KSDI_dn(n) = ln(L / max(H, n)) / sigma_n
    PeakOsc    = mean over n in {5,10,...,50} of (KSDI_up(n) - KSDI_dn(n))
    KaseCD     = PeakOsc - SMA(PeakOsc, 9)
    PeakMax    = max(2 * rolling-100 stddev of PeakOsc,
                     90th percentile of |PeakOsc| over rolling 250)
    PeakMin    = min of the same two quantities

Note on sign: ln(H / min L) >= 0 and ln(L / max H) <= 0 by
construction, so KSDI_up - KSDI_dn >= 0 and PeakOsc >= 0 always.
The PeakOsc level itself never crosses zero -- the zero-crossing
signal lives in KaseCD (PeakOsc minus its own 9-bar SMA). PeakMax
is therefore the operative overextension bound for longs; the
mirror short PeakOut (PeakOsc below -PeakMax) cannot fire given
PeakOsc >= 0, so the effective short exit is the opposite KCD
cross. PeakMin is computed and exposed (0 <= PeakMin <= PeakMax)
but is not used by the shipped signals; see README/CALIBRATION.

Columns:

    kase_peak_osc, kase_cd, kase_peak_max, kase_peak_min, atr
    (plus per-n KSDI columns are not kept; only the aggregates)

No lookahead: every rolling window ends on bar j; SMA(9) of PeakOsc
uses PeakOsc through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

KSDI_NS = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50)
KCD_SMA_N = 9
PEAK_STD_N = 100
PEAK_PCT_N = 250
PEAK_PCT_Q = 0.90


def _log_returns(c: pd.Series) -> pd.Series:
    return np.log(c / c.shift(1))


def kase_peak(df: pd.DataFrame, ns=KSDI_NS,
              kcd_n: int = KCD_SMA_N) -> pd.DataFrame:
    """PeakOscillator and KaseCD from the OHLC frame."""
    h = df["h"]
    l = df["l"]
    c = df["c"]
    r = _log_returns(c)

    ksdi_diffs = []
    for n in ns:
        sigma = r.rolling(n, min_periods=n).std()
        sigma = sigma.replace(0.0, np.nan)
        up = np.log(h / l.rolling(n, min_periods=n).min()) / sigma
        dn = np.log(l / h.rolling(n, min_periods=n).max()) / sigma
        ksdi_diffs.append(up - dn)
    # mean with min_count=10: PeakOsc is NaN until ALL ten KSDI horizons
    # are formed (the n=50 leg, ~51 bars). The default skipna mean would
    # silently average only the short horizons during spin-up.
    stacked = pd.concat(ksdi_diffs, axis=1)
    peak_osc = stacked.mean(axis=1).where(stacked.notna().sum(axis=1) == len(ns))
    kase_cd = peak_osc - B.sma(peak_osc, kcd_n)

    std100 = peak_osc.rolling(PEAK_STD_N, min_periods=PEAK_STD_N).std()
    pct250 = peak_osc.abs().rolling(PEAK_PCT_N, min_periods=PEAK_PCT_N).quantile(PEAK_PCT_Q)
    # np.maximum/minimum propagate NaN: PeakMax is NaN until BOTH the
    # rolling-100 stddev and the rolling-250 percentile are formed
    # (~254 bars). concat(...).max(axis=1) would skipna and fake an
    # early bound from the stddev leg alone.
    peak_max = np.maximum(2.0 * std100, pct250)
    peak_min = np.minimum(2.0 * std100, pct250)

    return pd.DataFrame({
        "kase_peak_osc": peak_osc,
        "kase_cd": kase_cd,
        "kase_peak_max": peak_max,
        "kase_peak_min": peak_min,
    })


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = kase_peak(df)
    for col in k.columns:
        df[col] = k[col]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
