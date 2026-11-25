"""Traders Dynamic Index (TDI) indicators (Dean Malone).

    rsi         = RSI(13) (Wilder)
    price line  = SMA(RSI, 2)
    signal line = SMA(RSI, 7)
    base line   = SMA(RSI, 34)
    vol bands   = base +/- 1.6185 * std(RSI, 34)

All inputs are causal (Wilder RSI is a causal ewm; SMAs and
the rolling std use data through bar i only), so every value
on bar i uses data through bar i's close only. The bands are
computed and stored for charting/context; the shipped signals
use the price/signal cross plus the base-line level filter.

Columns:
    tdi_rsi, tdi_price, tdi_signal, tdi_base,
    tdi_band_upper, tdi_band_lower, atr
"""

import pandas as pd

from strategies import base as B

RSI_N = 13
PRICE_N = 2
SIGNAL_N = 7
BASE_N = 34
BAND_MULT = 1.6185


def add_indicators(
    df: pd.DataFrame,
    rsi_n: int = RSI_N,
    price_n: int = PRICE_N,
    signal_n: int = SIGNAL_N,
    base_n: int = BASE_N,
    band_mult: float = BAND_MULT,
) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], rsi_n)
    df["tdi_rsi"] = rsi
    df["tdi_price"] = B.sma(rsi, price_n)
    df["tdi_signal"] = B.sma(rsi, signal_n)
    df["tdi_base"] = B.sma(rsi, base_n)
    sd = rsi.rolling(base_n, min_periods=base_n).std()
    df["tdi_band_upper"] = df["tdi_base"] + band_mult * sd
    df["tdi_band_lower"] = df["tdi_base"] - band_mult * sd
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
