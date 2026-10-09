"""Opening-range breakout indicators.

Source: ibrahimshere/nq-l2-scalping "Strategy 020" — winner of an internal
strategy bake-off (profit factor 8.0 on 34 NQ trades): tight consolidation
during a short opening range, then breakout with a wide TP / tight SL
(8:1 risk-reward in the original).

Crypto adaptation: 24/7 market has no RTH open, so the "opening range" is
the first 4 hourly bars of each UTC day. Risk-reward adapted to 3:1
(3xATR target / 1xATR stop) — 8:1 on 1h crypto would almost never fill.
https://github.com/ibrahimshere/nq-l2-scalping/blob/HEAD/data/l2_winner_candidates.md
"""

import pandas as pd

from strategies import base as B

OR_BARS = 4  # first 4 hours of the UTC day form the opening range


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    day = pd.to_datetime(df["t"], unit="ms", utc=True).dt.floor("D")
    df["_day"] = day
    df["_bar_in_day"] = df.groupby("_day").cumcount()
    or_high = df[df["_bar_in_day"] < OR_BARS].groupby("_day")["h"].max()
    or_low = df[df["_bar_in_day"] < OR_BARS].groupby("_day")["l"].min()
    df["or_high"] = df["_day"].map(or_high).shift(0)
    df["or_low"] = df["_day"].map(or_low).shift(0)
    # OR is only known after its 4 bars complete
    df.loc[df["_bar_in_day"] < OR_BARS, ["or_high", "or_low"]] = float("nan")
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df.drop(columns=["_day", "_bar_in_day"])
