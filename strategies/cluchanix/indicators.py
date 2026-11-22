"""ClucHAnix indicators (freqtrade, ssssi/freqtrade_strs).

Pipeline, computed bar by bar using only data through bar i:

1. Heikin Ashi candles from the raw OHLC (recursive ha_open, so each
   bar's HA values depend only on bars <= i).
2. Bollinger Bands (40, 2 sigma) on the Heikin Ashi typical price
   (ha_high + ha_low + ha_close) / 3 -> mid / lower / upper.
3. bbdelta = |mid - lower|; closedelta = |ha_close - ha_close[-1]|;
   tail = |ha_close - ha_low| (long side) and tail_up =
   |ha_high - ha_close| (short mirror).
4. EMA(3) / EMA(50) on ha_close.
5. RSI(14) on the regular close, Fisher-transformed exactly as in
   the source: fisher = tanh(0.1 * (rsi - 50)).
6. ROCR(28) = ha_close / ha_close[-28] on this timeframe, and
   ROCR(168) = ha_close / ha_close[-168] — the source's 1h
   informative ROCR(168); on 1h bars the 168-bar lookback IS the
   1h informative series (7 days of 1h closes), so no resampling
   is needed and nothing from the future is read.

No lookahead: every column at bar i is a function of bars <= i
(HA recursion, rolling windows, shifts of 1+ bars only). The
strategy was written for 1m bars; here it runs on 1h bars with
the published hyperopt constants unchanged (see CALIBRATION.md).
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_WINDOW = 40
BB_STD = 2.0
EMA_FAST = 3
EMA_SLOW = 50
ROCR_FAST = 28
ROCR_1H = 168

# Published hyperopt constants, ClucHAnix.py buy_params / sell_params.
BBDELTA_CLOSE = 0.01965
CLOSEDDELTA_CLOSE = 0.00556
BBDELTA_TAIL = 0.95089
CLOSE_BBLOWER = 0.00799
ROCR_1H_MIN = 0.54904
SELL_FISHER = 0.38414
SELL_BBMIDDLE_CLOSE = 1.07634


def _heikin_ashi(o, h, l, c):
    """Causal Heikin Ashi: ha_open[i] uses ha_open[i-1], ha_close[i-1]."""
    n = len(c)
    ha_close = (o + h + l + c) / 4.0
    ha_open = np.empty(n, dtype=float)
    ha_open[0] = (o[0] + c[0]) / 2.0
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    ha_high = np.maximum(np.maximum(h, ha_open), ha_close)
    ha_low = np.minimum(np.minimum(l, ha_open), ha_close)
    return ha_open, ha_high, ha_low, ha_close


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    ha_open, ha_high, ha_low, ha_close = _heikin_ashi(o, h, l, c)
    df["ha_open"] = ha_open
    df["ha_high"] = ha_high
    df["ha_low"] = ha_low
    df["ha_close"] = ha_close

    ha_typ = pd.Series(
        (ha_high + ha_low + ha_close) / 3.0, index=df.index
    )
    bb = B.bollinger(ha_typ, BB_WINDOW, BB_STD)
    df["mid"] = bb["bb_mid"]
    df["lower"] = bb["bb_lower"]
    df["upper"] = bb["bb_upper"]

    df["bbdelta"] = (df["mid"] - df["lower"]).abs()
    ha_close_s = pd.Series(ha_close, index=df.index)
    df["closedelta"] = (ha_close_s - ha_close_s.shift(1)).abs()
    df["tail"] = (ha_close_s - pd.Series(ha_low, index=df.index)).abs()
    df["tail_up"] = (pd.Series(ha_high, index=df.index) - ha_close_s).abs()

    df["ema_fast"] = B.ema(ha_close_s, EMA_FAST)
    df["ema_slow"] = B.ema(ha_close_s, EMA_SLOW)

    rsi = B.rsi(df["c"], 14)
    df["rsi"] = rsi
    df["fisher"] = np.tanh(0.1 * (rsi - 50.0))

    df["rocr"] = ha_close_s / ha_close_s.shift(ROCR_FAST)
    df["rocr_1h"] = ha_close_s / ha_close_s.shift(ROCR_1H)

    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
