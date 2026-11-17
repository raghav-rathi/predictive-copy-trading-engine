"""Ichimoku + MACD indicators.

Ichimoku (Tenkan 9, Kijun 26, Senkou B 52, displacement 26) via
the shared ``strategies.base.ichimoku`` helper, and MACD(12, 26, 9)
via ``strategies.base.macd``.

Cloud-alignment choice (see CALIBRATION.md): the cloud columns
``senkou_a`` / ``senkou_b`` are used EXACTLY as the helper returns
them — i.e. the leading spans as PLOTTED at bar i, displaced 26
bars forward. A value plotted at bar i is computed from data
ending at bar i-26, so it is fully causal at bar i; it is NOT
shifted back to the bar it was computed from. The Chikou span is
deliberately NOT shipped: the helper computes it as
``close.shift(-26)``, which reads 26 bars into the future and
would be lookahead.

Columns:

    tenkan       -- (highest high + lowest low) / 2 over 9 bars
    kijun        -- (highest high + lowest low) / 2 over 26 bars
    senkou_a     -- (tenkan + kijun) / 2, displaced +26 bars
                    (value plotted at bar i, from data to i-26)
    senkou_b     -- (highest high + lowest low) / 2 over 52 bars,
                    displaced +26 bars (same reading)
    macd         -- MACD line (EMA12 - EMA26)
    macd_signal  -- EMA9 of the MACD line
    macd_hist    -- MACD line - signal line
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only (the displaced cloud values use data through bar i-26).
"""

import pandas as pd

from strategies import base as B

TENKAN_N = 9
KIJUN_N = 26
SENKOU_N = 52
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["tenkan", "kijun", "senkou_a", "senkou_b",
                  "macd", "macd_signal", "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ichi = B.ichimoku(df["h"], df["l"], df["c"],
                      tenkan=TENKAN_N, kijun=KIJUN_N, senkou=SENKOU_N)
    df["tenkan"] = ichi["tenkan"]
    df["kijun"] = ichi["kijun"]
    df["senkou_a"] = ichi["senkou_a"]
    df["senkou_b"] = ichi["senkou_b"]
    # Chikou span deliberately NOT copied: it is close.shift(-26)
    # (26 bars into the future) and would be lookahead.
    m = B.macd(df["c"], fast=MACD_FAST, slow=MACD_SLOW,
               signal=MACD_SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
