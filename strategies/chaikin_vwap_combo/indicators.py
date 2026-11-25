"""Chaikin Money Flow + session VWAP indicators (Marc Chaikin).

StockCharts ChartSchool, "Chaikin Money Flow (CMF)":

    Money Flow Multiplier = ((Close - Low) - (High - Close)) / (High - Low)
    Money Flow Volume     = Money Flow Multiplier * Volume
    CMF(20)               = Sum(Money Flow Volume, 20) / Sum(Volume, 20)

The multiplier is 0 when High == Low (a zero-range bar carries no
money-flow information). CMF ranges from -1 to +1; above zero is
accumulation (buying pressure), below zero distribution. The
20-bar window is the StockCharts/TradingView default (Chaikin's
original used 21 days).

Session VWAP is the UTC-day anchored VWAP from base.anchored_vwap:
the day's volume-weighted average price, resetting at 00:00 UTC.

Columns:
    mfm      -- money flow multiplier
    mfv      -- money flow volume
    cmf      -- CMF(20)
    vwap_day -- UTC-day anchored VWAP
    atr      -- Wilder ATR(14), for the risk layer

No lookahead: every column is a rolling sum / cumulative sum of
bars up to and including the current bar.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CMF_WINDOW = 20  # shipped default (StockCharts/TradingView default)


def add_indicators(
    df: pd.DataFrame,
    cmf_window: int = CMF_WINDOW,
) -> pd.DataFrame:
    df = df.copy()
    rng = df["h"] - df["l"]
    df["mfm"] = np.where(
        rng == 0,
        0.0,
        ((df["c"] - df["l"]) - (df["h"] - df["c"])) / rng.replace(0, np.nan),
    )
    df["mfv"] = df["mfm"] * df["v"]
    df["cmf"] = (
        df["mfv"].rolling(cmf_window, min_periods=cmf_window).sum()
        / df["v"].rolling(cmf_window, min_periods=cmf_window).sum()
    )
    df["vwap_day"] = B.anchored_vwap(df["h"], df["l"], df["c"], df["v"], df["t"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
