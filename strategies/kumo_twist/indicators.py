"""Ichimoku Kumo (cloud) twist indicators.

Senkou Span A = (Tenkan-sen + Kijun-sen) / 2.
Senkou Span B = (highest high + lowest low over 52 bars) / 2.
Tenkan-sen(9) and Kijun-sen(26) are the standard rolling midpoints,
reused from the shared strategies.base.ichimoku() helper.

CAUSALITY NOTE — NO forward displacement: in textbook Ichimoku both
spans are PLOTTED 26 bars ahead of the bar they are computed from, so
the cloud you see at bar i was computed from data through bar i-26.
This strategy does NOT use the displaced (plotted) values. The spans
here are evaluated at bar i from data through bar i — i.e. the cloud
as known at bar i, with no 26-bar shift in either direction. A twist
is therefore a cross of the two current, causal span values, and no
future data enters the signal. The shared helper's shifted senkou
columns (and its Chikou span, shifted -26) are NOT used.
"""

import pandas as pd

from strategies.base import ichimoku

TENKAN_PERIOD = 9
KIJUN_PERIOD = 26
SENKOU_PERIOD = 52

INDICATOR_COLS = [
    "tenkan",
    "kijun",
    "senkou_a",
    "senkou_b",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ich = ichimoku(df["h"], df["l"], df["c"], TENKAN_PERIOD, KIJUN_PERIOD, SENKOU_PERIOD)
    df["tenkan"] = ich["tenkan"]
    df["kijun"] = ich["kijun"]
    # Unshifted spans: values as known at bar i, NOT plotted 26 bars ahead.
    df["senkou_a"] = (df["tenkan"] + df["kijun"]) / 2
    df["senkou_b"] = (
        df["h"].rolling(SENKOU_PERIOD, min_periods=SENKOU_PERIOD).max()
        + df["l"].rolling(SENKOU_PERIOD, min_periods=SENKOU_PERIOD).min()
    ) / 2
    return df
