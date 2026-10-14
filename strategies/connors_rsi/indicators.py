"""Connors RSI(2) pullback indicators (Larry Connors, Short-Term Trading
Strategies That Work, "R3" system).

Ingredients:
  - RSI(2) of close: the short-horizon mean-reversion gauge.
  - SMA(200) of close: the long-horizon trend filter.
  - SMA(50) of close: the regime filter (longs invalidated below it).
  - ATR(14): stop sizing (used by risk.py, not by the signal logic).
  - decline/rise streaks: n consecutive down/up bars in the RSI(2) series
    ending at the current bar, for the "3-bar decline into RSI2<10" entry.

No lookahead: every value uses only bars through the current close.
RSI/SMA are forward-recursive or trailing rolling windows, so truncation
of the frame leaves values at the truncation bar unchanged.
"""

import pandas as pd

from strategies import base as B

RSI_N = 2
SMA_TREND_N = 200
SMA_EXIT_N = 50
ATR_N = 14
STREAK = 3


def streak_down(s: pd.Series, n: int = STREAK) -> pd.Series:
    """True where s has declined n consecutive bars ending at the current bar.

    I.e. s[i] < s[i-1] < ... < s[i-n] with s[i] the current bar.
    """
    out = pd.Series(True, index=s.index)
    for k in range(n):
        out &= s.shift(k) < s.shift(k + 1)
    return out.fillna(False)


def streak_up(s: pd.Series, n: int = STREAK) -> pd.Series:
    """True where s has risen n consecutive bars ending at the current bar."""
    out = pd.Series(True, index=s.index)
    for k in range(n):
        out &= s.shift(k) > s.shift(k + 1)
    return out.fillna(False)


def add_indicators(
    df: pd.DataFrame,
    rsi_n: int = RSI_N,
    sma_trend_n: int = SMA_TREND_N,
    sma_exit_n: int = SMA_EXIT_N,
    streak: int = STREAK,
) -> pd.DataFrame:
    df = df.copy()
    df["rsi2"] = B.rsi(df["c"], rsi_n)
    df["sma200"] = B.sma(df["c"], sma_trend_n)
    df["sma50"] = B.sma(df["c"], sma_exit_n)
    df["decl3"] = streak_down(df["rsi2"], streak)
    df["rise3"] = streak_up(df["rsi2"], streak)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
