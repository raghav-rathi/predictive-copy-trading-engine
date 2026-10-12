"""Dual-Bear Pullback Short indicators.

Mechanism (ported from zhangyong78/qqokx btc_ema_short_research
results_v3_exit_study — OKX BTC-USDT-SWAP 2019-2026; the study's key
finding is that the EXIT (reclaim of 4H EMA21) matters most). Short-only
BTC framework adapted to 1h Hyperliquid bars:

  resample: 1h bars are aggregated to daily and 4h bars inside
      add_indicators; the aggregates are forward-filled onto the 1h
      index. Multi-timeframe series that must be *complete* are shifted
      by one period at the resampled level (no lookahead); the
      developing daily/4h values used are functions of bars through the
      current 1h close only.
  daily regime gate (ALL must hold for a short to be admitted):
      daily EMA21 < daily EMA55 (last complete day),
      developing daily close (current 1h close) < daily EMA55,
      last complete day's volume >= its 20-day volume SMA.
  4H entry trigger (evaluated on the first 1h bar of each new 4H block,
      i.e. when a new complete 4H bar prints):
      two consecutive complete 4H bear bars (close < open), with the
      trigger bar (latest complete) pulling back up toward 4H EMA21:
      0 <= EMA21_4h - close_trigger <= 0.5 * ATR(14, 1h) (from below),
      and trigger-bar 4H volume > its 20-period SMA.
  exit: 4H price reclaims 4H EMA21 — developing 4H close (== current 1h
      close) > developing 4H EMA21.

No lookahead: every column on 1h bar i uses only data through bar i's
close. Verified by the truncation unit test.
"""

import numpy as np
import pandas as pd

from strategies import base as B

HOUR_MS = 3_600_000
BLOCK_MS = 4 * HOUR_MS
DAY_MS = 86_400_000

DAILY_EMA_FAST = 21
DAILY_EMA_SLOW = 55
DAILY_VOL_N = 20
H4_EMA = 21
H4_VOL_N = 20
PULLBACK_ATR_MULT = 0.5  # trigger bar must close within 0.5xATR below 4H EMA21
ATR_N = 14


def _ohlcv_agg(g):
    return pd.DataFrame({
        "o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(),
        "c": g["c"].last(), "v": g["v"].sum()})


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    block = (df["t"] // BLOCK_MS).to_numpy()
    day = (df["t"] // DAY_MS).to_numpy()
    blk_s = pd.Series(block, index=df.index)
    day_s = pd.Series(day, index=df.index)

    # --- 4H aggregates ---------------------------------------------------
    h4 = _ohlcv_agg(df.assign(_b=block).groupby("_b")).sort_index()
    h4c = h4.shift(1)  # complete 4H bars only
    h4_ema21 = B.ema(h4c["c"], H4_EMA)
    h4_vol_sma = h4c["v"].rolling(H4_VOL_N, min_periods=H4_VOL_N).mean()
    bear1 = (h4c["c"] < h4c["o"])
    bear2 = (h4c["c"] < h4c["o"]).shift(1)
    df["h4_two_bear"] = blk_s.map(bear1 & bear2).fillna(False).astype(bool)
    df["h4_ema21"] = blk_s.map(h4_ema21).astype(float)
    df["h4_trig_close"] = blk_s.map(h4c["c"]).astype(float)
    df["h4_vol_ok"] = (blk_s.map(h4c["v"]) > blk_s.map(h4_vol_sma)
                       ).fillna(False).astype(bool)
    # developing 4H EMA21 for the reclaim exit (uses data through this bar)
    h4_ema21_dev = B.ema(h4["c"], H4_EMA)
    df["h4_ema21_dev"] = blk_s.map(h4_ema21_dev).astype(float)

    # --- daily aggregates (complete days) --------------------------------
    d1 = _ohlcv_agg(df.assign(_d=day).groupby("_d")).sort_index()
    d1c = d1.shift(1)
    dema21 = B.ema(d1c["c"], DAILY_EMA_FAST)
    dema55 = B.ema(d1c["c"], DAILY_EMA_SLOW)
    dvol = d1c["v"]
    dvol_sma = dvol.rolling(DAILY_VOL_N, min_periods=DAILY_VOL_N).mean()
    df["d_ema21"] = day_s.map(dema21).astype(float)
    df["d_ema55"] = day_s.map(dema55).astype(float)
    df["d_vol_ok"] = (day_s.map(dvol) >= day_s.map(dvol_sma)
                      ).fillna(False).astype(bool)

    # --- 1h-level ----------------------------------------------------------
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    df["new_block"] = (blk_s != blk_s.shift(1)).fillna(True)

    # pullback distance of the trigger bar below 4H EMA21 (only meaningful
    # on new-block bars; evaluated there)
    gap = df["h4_ema21"] - df["h4_trig_close"]
    df["pullback_ok"] = (
        df["new_block"] & (gap >= 0) & (gap <= PULLBACK_ATR_MULT * df["atr"])
        & df["h4_ema21"].notna() & df["atr"].notna()
    ).fillna(False).astype(bool)

    # daily regime gate
    df["regime_ok"] = (
        (df["d_ema21"] < df["d_ema55"])
        & (df["c"] < df["d_ema55"])      # developing daily close < EMA55
        & df["d_vol_ok"]
        & df["d_ema21"].notna() & df["d_ema55"].notna()
    ).fillna(False).astype(bool)
    return df
