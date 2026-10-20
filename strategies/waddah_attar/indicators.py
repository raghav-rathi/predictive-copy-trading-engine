"""Ahmad Waddah Attar's Waddah Attar Explosion (WAE) indicators.

Components (per the author's own entry/exit rules):
  macd      = EMA(Close, 20) - EMA(Close, 40)
  hist      = SENS * (macd - macd.shift(1))      -- momentum acceleration,
                                                    sensitivity 150
  explosion = EXP_MULT * stdev(hist, EXP_LEN)    -- volatility-scaled
                                                    momentum band
  dead      = DEAD_MULT * ATR(100)               -- "dead zone" filter;
                                                    trades only print
                                                    when hist and the
                                                    explosion line are
                                                    above it

A long prints when the histogram is positive, rising, above the
explosion line, with a rising explosion line, and both histogram and
explosion clear the dead zone. The short side mirrors (negative,
falling). Exits when the histogram falls back under the explosion line.

No lookahead: every column on bar i uses data through i only.
"""

import pandas as pd

from strategies import base as B

EMA_FAST = 20
EMA_SLOW = 40
SENS = 150.0
EXP_MULT = 2.0
EXP_LEN = 20
DEAD_MULT = 3.7
DEAD_ATR_N = 100


def add_indicators(
    df: pd.DataFrame,
    ema_fast: int = EMA_FAST,
    ema_slow: int = EMA_SLOW,
    sens: float = SENS,
    exp_mult: float = EXP_MULT,
    exp_len: int = EXP_LEN,
    dead_mult: float = DEAD_MULT,
    dead_atr_n: int = DEAD_ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    macd = B.ema(df["c"], ema_fast) - B.ema(df["c"], ema_slow)
    hist = sens * (macd - macd.shift(1))
    df["wae_hist"] = hist
    df["wae_expl"] = exp_mult * hist.rolling(exp_len, min_periods=exp_len).std()
    df["wae_dead"] = dead_mult * B.atr(df["h"], df["l"], df["c"], dead_atr_n)
    df["wae_hist_rising"] = hist > hist.shift(1)
    df["wae_expl_rising"] = df["wae_expl"] > df["wae_expl"].shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
