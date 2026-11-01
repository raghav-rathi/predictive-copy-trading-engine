"""Central Pivot Range indicators (Frank Ochoa).

Each UTC day's high, low, and last close define the next day's levels:
Pivot = (H+L+C)/3, BC = (H+L)/2, TC = 2*Pivot - BC. The TC-BC zone is
the market's value area: closes above TC are bullish, below BC are
bearish, and a narrow zone forecasts an explosive day.

Columns:
    cpr_pivot -- prior UTC day's Pivot, forward-filled across the day
    cpr_tc    -- prior UTC day's Top Central pivot
    cpr_bc    -- prior UTC day's Bottom Central pivot
    atr       -- Wilder ATR(14) for the risk layer

Levels are computed from completed days only and forward-filled, so
no bar ever reads its own day's unfinished high/low/close: strictly
causal.
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    days = (df["t"].to_numpy(dtype="int64") // 86_400_000)
    daily = pd.DataFrame({"day": days, "h": df["h"].to_numpy(),
                          "l": df["l"].to_numpy(), "c": df["c"].to_numpy()})
    agg = daily.groupby("day").agg(H=("h", "max"), L=("l", "min"),
                                   C=("c", "last"))
    pivot = (agg["H"] + agg["L"] + agg["C"]) / 3.0
    bc = (agg["H"] + agg["L"]) / 2.0
    tc = 2.0 * pivot - bc
    levels = pd.DataFrame({"cpr_pivot": pivot, "cpr_tc": tc, "cpr_bc": bc})
    levels = levels.shift(1)  # prior day's levels apply today
    mapped = pd.DataFrame({"day": days}).merge(
        levels, left_on="day", right_index=True, how="left")
    df["cpr_pivot"] = mapped["cpr_pivot"].to_numpy()
    df["cpr_tc"] = mapped["cpr_tc"].to_numpy()
    df["cpr_bc"] = mapped["cpr_bc"].to_numpy()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
