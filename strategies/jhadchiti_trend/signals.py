"""jhadchiti trend signals.

LONG when ALL of:
  (a) close > highest close of the last 55 bars (breakout),
  (b) BTC SMA(200) rising vs 20 bars ago (regime, 1h adaptation of the
      author's daily rule),
  (c) |hourly funding| <= 0.00025 (not dangerously crowded),
  (d) coin's 30-bar return > BTC's 30-bar return (universe-filter adaptation).
SHORT is the mirror (BTC regime inverted, coin underperforms BTC).

Exit on ANY of: close crosses the 20-period close channel against the
position; the harness's 2xATR(20) stop; 2160-bar (90-day) max hold.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    regime_up = df["btc_regime_up"].fillna(False)
    fund_ok = df["fund_ok"].fillna(False)
    mom_lead = (df["ret30"] > df["btc_ret30"]).fillna(False)
    mom_lag = (df["ret30"] < df["btc_ret30"]).fillna(False)

    df["long_entry"] = (
        (df["c"] > df["chan55_hi"]) & regime_up & fund_ok & mom_lead
    )
    df["short_entry"] = (
        (df["c"] < df["chan55_lo"]) & (~regime_up) & fund_ok & mom_lag
    )
    df["long_exit"] = B.crossed_below(df["c"], df["chan20_lo"])
    df["short_exit"] = B.crossed_above(df["c"], df["chan20_hi"])

    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
