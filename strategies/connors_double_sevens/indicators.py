"""Connors Double 7s indicators.

Larry Connors & Cesar Alvarez's Double 7s system, from "Short Term
Trading Strategies That Work". The system's "days" are UTC calendar
days, so the 1h frame is resampled to daily closes (last close of
each UTC day) and the daily statistics are mapped back onto the 1h
bars.

Daily quantities (all causal within the daily series):
  daily_close : last close of each UTC day
  sma200      : SMA(200) of daily closes
  low7        : lowest daily close of the last 7 days (incl. today)
  high7       : highest daily close of the last 7 days (incl. today)

On the 1h frame each quantity is populated only on the last bar of
its UTC day (the 23:00 UTC bar, whose close IS that day's close) and
forward-filled to later bars, so a bar never carries a daily value
that was not known by that bar's close. ``is_day_close`` flags the
last bar of each UTC day; signals are only evaluated on those bars.
"""

import pandas as pd

SMA_WINDOW = 200
LOW_HIGH_WINDOW = 7

INDICATOR_COLS = [
    "daily_close",
    "sma200_daily",
    "low7_daily",
    "high7_daily",
    "is_day_close",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    day = ts.dt.floor("D")

    # Daily closes: last close of each UTC day.
    daily = df.groupby(day.values)["c"].last()
    daily.index = pd.DatetimeIndex(daily.index, tz="UTC")

    sma200 = daily.rolling(SMA_WINDOW, min_periods=SMA_WINDOW).mean()
    low7 = daily.rolling(LOW_HIGH_WINDOW, min_periods=LOW_HIGH_WINDOW).min()
    high7 = daily.rolling(LOW_HIGH_WINDOW, min_periods=LOW_HIGH_WINDOW).max()

    # Map each bar to its own day's daily statistics, then keep the
    # value only on the last bar of the day and forward-fill, so no
    # bar sees a daily value before that day has closed.
    bar_day = pd.DatetimeIndex(day.values, tz="UTC")
    daily_close_bar = daily.reindex(bar_day).to_numpy(dtype=float)
    sma_bar = sma200.reindex(bar_day).to_numpy(dtype=float)
    low7_bar = low7.reindex(bar_day).to_numpy(dtype=float)
    high7_bar = high7.reindex(bar_day).to_numpy(dtype=float)

    last_idx = df.assign(_day=day.values).groupby("_day").tail(1).index
    is_day_close = pd.Series(False, index=df.index)
    is_day_close.loc[last_idx] = True

    def _day_close_only(values):
        s = pd.Series(values, index=df.index, dtype=float)
        s = s.where(is_day_close).ffill()
        return s

    df["daily_close"] = _day_close_only(daily_close_bar)
    df["sma200_daily"] = _day_close_only(sma_bar)
    df["low7_daily"] = _day_close_only(low7_bar)
    df["high7_daily"] = _day_close_only(high7_bar)
    df["is_day_close"] = is_day_close.astype(bool)
    return df
