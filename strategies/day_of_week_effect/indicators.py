"""Day-of-week effect indicators.

Fixed from the literature (Decourt, Chohan & Perugini 2017;
Caporale & Plastun 2018; FairHatch 2026 Binance daily data):
Bitcoin's weekday seasonality -- Mondays relatively strong,
Thursdays the weakest weekday. The shipped config is LONG
Mondays, SHORT Thursdays (UTC).

Per-bar columns (pure functions of the UTC timestamp, plus
Wilder ATR(14) for risk):

    weekday -- pandas weekday, Monday=0 .. Sunday=6
    hour    -- UTC hour 0..23
    atr14   -- Wilder ATR(14) for risk

No lookahead: weekday/hour come only from the bar's own
timestamp; ATR is Wilder smoothing.
"""

import pandas as pd

from strategies import base as B

ATR_N = 14


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["weekday"] = ts.dt.weekday.to_numpy(int)
    df["hour"] = ts.dt.hour.to_numpy(int)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
