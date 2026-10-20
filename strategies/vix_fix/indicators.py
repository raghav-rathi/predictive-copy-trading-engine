"""Larry Williams' VIX Fix (WVF) fear-spike indicators.

WVF ("Williams VIX Fix") synthesizes a VIX-like fear gauge from price
alone:

    WVF = 100 * (Highest(High, 22) - Low) / Highest(High, 22)

A Bollinger Band (length 20, mult 2.0) is drawn on WVF. A cross of WVF
above the upper band marks an extreme fear spike (the classic Larry
Williams market-bottom setup).

The inverse leg ("iWVF", greed extreme) is a mirrored construction used
for the short side:

    iWVF = 100 * (High - Lowest(Low, 22)) / Lowest(Low, 22)

A cross of iWVF above ITS upper band marks extreme greed / blow-off.
This inverse leg is the less-reliable published variant and is
documented as such in BACKTEST.md.

No lookahead: every column on bar i uses highs/lows/closes through i
only. WVF is bounded in [0, 100] (for positive highs).
"""

import pandas as pd

from strategies import base as B

WVF_LEN = 22
BB_LEN = 20
BB_MULT = 2.0
ATR_N = 14


def _wvf(high: pd.Series, low: pd.Series, n: int) -> pd.Series:
    highest = high.rolling(n, min_periods=n).max()
    return 100.0 * (highest - low) / highest


def _iwvf(high: pd.Series, low: pd.Series, n: int) -> pd.Series:
    lowest = low.rolling(n, min_periods=n).min()
    return 100.0 * (high - lowest) / lowest


def add_indicators(
    df: pd.DataFrame,
    wvf_len: int = WVF_LEN,
    bb_len: int = BB_LEN,
    bb_mult: float = BB_MULT,
) -> pd.DataFrame:
    df = df.copy()
    df["wvf"] = _wvf(df["h"], df["l"], wvf_len)
    bb = B.bollinger(df["wvf"], bb_len, bb_mult)
    df["wvf_bb_mid"] = bb["bb_mid"]
    df["wvf_bb_upper"] = bb["bb_upper"]
    df["wvf_bb_lower"] = bb["bb_lower"]
    df["iwvf"] = _iwvf(df["h"], df["l"], wvf_len)
    ibb = B.bollinger(df["iwvf"], bb_len, bb_mult)
    df["iwvf_bb_mid"] = ibb["bb_mid"]
    df["iwvf_bb_upper"] = ibb["bb_upper"]
    df["iwvf_bb_lower"] = ibb["bb_lower"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
