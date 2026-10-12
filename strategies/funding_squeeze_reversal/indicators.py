"""Funding Squeeze Reversal indicators.

Mechanism (ported from beatp-bit/funding-squeeze-reversal, MIT, CoinMarketCap
BNB HACK 2026): over-crowded leveraged perp positioning mean-reverts as
squeezes exhaust. Entry when the 8h cumulative hourly funding rate is
extreme AND volume is elevated (1.5x its 20-bar SMA) — a weighted
confidence >= CONF_MIN is required.

DEVIATION FROM AUTHOR'S SPEC (documented): the original repo uses an
OI-divergence term (funding extreme + OI moving the opposite way =
exhaustion). Hyperliquid's public API does not expose a historical OI
series, so the OI term is dropped. The volume gates below are the author's
own "violent OI move" guard translated to volume: skip entries when volume
spikes > 3x its 20-bar SMA (blowoff, not exhaustion).

Funding history comes from the public `fundingHistory` endpoint, merged
onto the 1h bars with an asof join. Pass a precomputed `funding` Series
(indexed by ms) to skip the network fetch (unit tests do this).

No lookahead: every column on bar i uses only data through bar i's close.
The 8h funding sum on bar i uses the 8 funding prints at/before bar i's
open (merge_asof backward), i.e. information available at bar i's close.
"""

import pandas as pd

from strategies import base as B
from strategies.funding_tilt.indicators import load_funding

# --- author-specified parameters (shipped) ---------------------------------
FUND_SHORT_THR = 0.00030   # +0.030% per 8h-equivalent cumulative funding
FUND_LONG_THR = -0.00020   # -0.020% per 8h-equivalent cumulative funding
FUND_WINDOW_H = 8
VOL_SMA_N = 20
VOL_MIN_RATIO = 1.5       # elevated volume gate
VOL_MAX_RATIO = 3.0       # violent-spike guard (author's OI guard -> volume)
CONF_MIN = 0.45           # weighted confidence gate
W_FUND = 0.6              # confidence weight: funding intensity
W_VOL = 0.4               # confidence weight: volume intensity


def add_indicators(df: pd.DataFrame, coin: str | None = None,
                   funding: pd.Series | None = None) -> pd.DataFrame:
    df = df.copy()
    if funding is None:
        if coin is None:
            raise ValueError("funding_squeeze_reversal.add_indicators needs coin= or funding=")
        funding = load_funding(coin, int(df["t"].min()) - 24 * 3_600_000,
                               int(df["t"].max()))
    funding.index.name = "t"
    fdf = funding.rename("funding").reset_index()
    df = pd.merge_asof(df.sort_values("t"), fdf.sort_values("t"),
                       on="t", direction="backward")
    df["fund8"] = df["funding"].rolling(FUND_WINDOW_H,
                                        min_periods=FUND_WINDOW_H).sum()
    df["vol_sma20"] = df["v"].rolling(VOL_SMA_N, min_periods=VOL_SMA_N).mean()
    df["vol_ratio"] = df["v"] / df["vol_sma20"].replace(0, float("nan"))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    # intensity terms in [0,1]: funding distance past the threshold (scaled
    # by 3x-threshold for full intensity), volume elevation past 1.5x
    fund_thr = df["fund8"].apply(
        lambda x: FUND_SHORT_THR if x >= 0 else abs(FUND_LONG_THR))
    fund_int = (df["fund8"].abs() / (3.0 * fund_thr)).clip(0.0, 1.0)
    vol_int = ((df["vol_ratio"] - VOL_MIN_RATIO) / VOL_MIN_RATIO).clip(0.0, 1.0)
    df["fsr_conf"] = W_FUND * fund_int + W_VOL * vol_int
    return df.sort_values("t").reset_index(drop=True)
