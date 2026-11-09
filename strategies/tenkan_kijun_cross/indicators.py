"""Ichimoku Tenkan-sen / Kijun-sen indicators.

Tenkan-sen = (highest high + lowest low over 9 bars) / 2.
Kijun-sen  = (highest high + lowest low over 26 bars) / 2.
Both are causal rolling midpoints (data through bar i only).

Reuses the shared strategies.base.ichimoku() helper, but only its
tenkan/kijun columns are copied into the frame. The helper also
computes the displaced Senkou spans and the Chikou span (which is
shifted -26, i.e. uses future closes); those columns are deliberately
NOT copied, so no lookahead enters this strategy.
"""

import pandas as pd

from strategies.base import ichimoku

TENKAN_PERIOD = 9
KIJUN_PERIOD = 26

INDICATOR_COLS = [
    "tenkan",
    "kijun",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ich = ichimoku(df["h"], df["l"], df["c"], TENKAN_PERIOD, KIJUN_PERIOD, 52)
    df["tenkan"] = ich["tenkan"]
    df["kijun"] = ich["kijun"]
    return df
