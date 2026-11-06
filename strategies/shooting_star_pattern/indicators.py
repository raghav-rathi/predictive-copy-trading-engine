"""Shooting star / inverted hammer indicators: EMA(20) trend context,
5-bar return, and single-candle shape (body, upper/lower shadows)."""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "ema20",
    "ret5",
    "body",
    "candle_range",
    "upper_shadow",
    "lower_shadow",
    "shooting_star",
    "inverted_hammer",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema20"] = B.ema(df["c"], 20)
    # 5-bar return through the prior bar (no lookahead in the context check).
    df["ret5"] = df["c"].shift(1) / df["c"].shift(6) - 1.0
    body_top = df[["o", "c"]].max(axis=1)
    body_bottom = df[["o", "c"]].min(axis=1)
    df["body"] = (df["c"] - df["o"]).abs()
    df["candle_range"] = df["h"] - df["l"]
    df["upper_shadow"] = df["h"] - body_top
    df["lower_shadow"] = body_bottom - df["l"]
    rng = df["candle_range"]
    body = df["body"]
    # Zero-range guard: no pattern on a zero-range bar.
    valid = rng > 0
    # Shooting star: small body in the lower third, long upper shadow.
    df["shooting_star"] = (
        valid
        & (body <= 0.30 * rng)
        & ((body_bottom - df["l"]) <= 0.35 * rng)
        & (df["upper_shadow"] >= 2.0 * body)
        & (df["lower_shadow"] <= 0.10 * rng)
    ).astype(bool)
    # Inverted hammer: small body in the upper third, long lower shadow.
    df["inverted_hammer"] = (
        valid
        & (body <= 0.30 * rng)
        & ((df["h"] - body_top) <= 0.35 * rng)
        & (df["lower_shadow"] >= 2.0 * body)
        & (df["upper_shadow"] <= 0.10 * rng)
    ).astype(bool)
    return df
