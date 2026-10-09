"""Donchian channel breakout (Turtle system) indicators.

Classic rules (public: "The Original Turtle Trading Rules"):
  entry channel 20 bars, exit channel 10 bars, 2xATR stop, 0.5xATR... here
  parameterized. ADX(14) > 20 regime filter added (competition-grade tweak:
  only trade breakouts when a trend regime is actually present).
"""

import pandas as pd

from strategies import base as B

ENTRY_N = 480  # 20 days on 1h bars — the true Turtle timeframe.
# Calibration 2026-10-09: 20/10-bar channels on 1h lost -15% (BTC) / -15%
# (ETH) over Mar-Oct 2026; the edge only appears at the daily scale
# (480/240: BTC +4.4%, Sharpe 0.74). Shorter channels trade noise.
EXIT_N = 240
ADX_N = 14
ADX_MIN = 20.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dc = B.donchian(df["h"], df["l"], ENTRY_N)
    df[f"dc_high_{ENTRY_N}"] = dc.iloc[:, 0]
    df[f"dc_low_{ENTRY_N}"] = dc.iloc[:, 1]
    dx = B.donchian(df["h"], df["l"], EXIT_N)
    df[f"dc_high_{EXIT_N}"] = dx.iloc[:, 0]
    df[f"dc_low_{EXIT_N}"] = dx.iloc[:, 1]
    # prior-bar channels: breakout confirmed at bar close vs channel formed
    # without the current bar (no lookahead)
    df["dc_high_entry"] = df[f"dc_high_{ENTRY_N}"].shift(1)
    df["dc_low_entry"] = df[f"dc_low_{ENTRY_N}"].shift(1)
    df["dc_high_exit"] = df[f"dc_high_{EXIT_N}"].shift(1)
    df["dc_low_exit"] = df[f"dc_low_{EXIT_N}"].shift(1)
    adx = B.adx(df["h"], df["l"], df["c"], ADX_N)
    df["adx"] = adx["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
