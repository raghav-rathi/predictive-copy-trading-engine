"""Larry Williams VIX Fix indicators.

WVF = 100 * (highest close over 22 bars - low) / highest close over 22 bars.
Upper band = SMA(20) of WVF + 2.0 * std(20) of WVF.
Range high = 0.85 * max WVF over the trailing 50 bars.
Green flash (fear spike) = WVF >= upper band OR WVF >= range high.

Inverted WVF: inv = 100 * (high - lowest close over 22 bars) /
lowest close over 22 bars, with its own upper band (SMA(20) +
2.0 * std(20)) and range high (0.85 * max inv over trailing 50).
Inverted flash = inv >= inv upper band OR inv >= inv range high.

Columns:
    wvf / wvf_upper / wvf_range_high -- Williams VIX Fix and its bands
    green_flash -- bool, fear spike on this bar
    inv_wvf / inv_upper / inv_range_high -- inverted VIX Fix and bands
    inv_flash -- bool, inverted fear spike on this bar
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. Rolling windows are trailing (include bar i, exclude later
bars). The standard deviation is the pandas sample std (ddof=1),
matching the template's Bollinger construction.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WVF_N = 22
BAND_N = 20
BAND_K = 2.0
RANGE_N = 50
RANGE_F = 0.85
ATR_N = 14


def add_indicators(df: pd.DataFrame, wvf_n: int = WVF_N,
                   band_n: int = BAND_N, band_k: float = BAND_K,
                   range_n: int = RANGE_N, range_f: float = RANGE_F,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    h = df["h"]
    l = df["l"]

    hc = c.rolling(wvf_n, min_periods=wvf_n).max()
    lc = c.rolling(wvf_n, min_periods=wvf_n).min()

    wvf = 100.0 * (hc - l) / hc.replace(0, np.nan)
    df["wvf"] = wvf
    wvf_mean = wvf.rolling(band_n, min_periods=band_n).mean()
    wvf_sd = wvf.rolling(band_n, min_periods=band_n).std()
    df["wvf_upper"] = wvf_mean + band_k * wvf_sd
    df["wvf_range_high"] = (
        range_f * wvf.rolling(range_n, min_periods=range_n).max()
    )
    df["green_flash"] = (
        (wvf >= df["wvf_upper"]) | (wvf >= df["wvf_range_high"])
    ).fillna(False).astype(bool)

    inv = 100.0 * (h - lc) / lc.replace(0, np.nan)
    df["inv_wvf"] = inv
    inv_mean = inv.rolling(band_n, min_periods=band_n).mean()
    inv_sd = inv.rolling(band_n, min_periods=band_n).std()
    df["inv_upper"] = inv_mean + band_k * inv_sd
    df["inv_range_high"] = (
        range_f * inv.rolling(range_n, min_periods=range_n).max()
    )
    df["inv_flash"] = (
        (inv >= df["inv_upper"]) | (inv >= df["inv_range_high"])
    ).fillna(False).astype(bool)

    df["atr"] = B.atr(h, l, c, atr_n)
    return df
