"""Asia Session Liquidation Sweep indicators.

Mechanism (ported from grahamovernightly/edgefindr Asia_Sweep_EA_spec.md):
liquidity swept from the prior session's extreme reverses into the next
session. All times UTC on 1h bars.
  sessions: Asia 00:00-07:00, London 07:00-12:00, NY 12:00-20:00
  bias: persistent 30-bar rolling swing break (BOS) — close above the
      rolling 30-bar high -> bullish (+1), below the rolling 30-bar
      low -> bearish (-1); bias holds until the opposite break. The
      rolling window excludes the current bar (shift(1)): no lookahead.
  reference levels: the just-completed session's extreme — today's Asia
      low/high feeds the London signal window, today's London low/high
      feeds the NY signal window. A session aggregate with < 5 bars
      (data gap) poisons the reference to NaN -> no signals.
No lookahead: every column on bar i uses only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MS_PER_DAY = 86_400_000
BOS_N = 30
MIN_SESSION_BARS = 5
ATR_N = 14

# signal windows (bar-open hour, UTC): London 07-10, NY 12-15 minus 14:00 skip
WINDOW_HOURS = {7, 8, 9, 12, 13}
KILL_HOUR = 20  # flat everything at the 20:00 UTC close


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["hour"] = ts.dt.hour.to_numpy()
    day = (df["t"] // MS_PER_DAY).to_numpy()
    df["day"] = day

    # --- session extremes ------------------------------------------------
    is_asia = df["hour"].between(0, 6)
    is_london = df["hour"].between(7, 11)
    tmp = df.assign(_day=day)
    asia = tmp[is_asia].groupby("_day").agg(
        asia_low=("l", "min"), asia_high=("h", "max"), asia_n=("c", "size"))
    london = tmp[is_london].groupby("_day").agg(
        lon_low=("l", "min"), lon_high=("h", "max"), lon_n=("c", "size"))
    asia_low = asia["asia_low"].where(asia["asia_n"] >= MIN_SESSION_BARS)
    asia_high = asia["asia_high"].where(asia["asia_n"] >= MIN_SESSION_BARS)
    lon_low = london["lon_low"].where(london["lon_n"] >= MIN_SESSION_BARS)
    lon_high = london["lon_high"].where(london["lon_n"] >= MIN_SESSION_BARS)

    day_s = pd.Series(day, index=df.index)
    in_london_win = df["hour"].isin([7, 8, 9])
    in_ny_win = df["hour"].isin([12, 13])
    df["ref_low"] = np.where(
        in_london_win, day_s.map(asia_low),
        np.where(in_ny_win, day_s.map(lon_low), np.nan)).astype(float)
    df["ref_high"] = np.where(
        in_london_win, day_s.map(asia_high),
        np.where(in_ny_win, day_s.map(lon_high), np.nan)).astype(float)

    # --- persistent BOS bias ---------------------------------------------
    hi30 = df["h"].rolling(BOS_N, min_periods=BOS_N).max().shift(1)
    lo30 = df["l"].rolling(BOS_N, min_periods=BOS_N).min().shift(1)
    sig = np.where(df["c"] > hi30, 1.0, np.where(df["c"] < lo30, -1.0, np.nan))
    df["bias"] = pd.Series(sig, index=df.index).ffill().fillna(0.0)

    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    df["kill_20"] = df["hour"] == KILL_HOUR
    df.drop(columns=["day"], inplace=True)
    return df
