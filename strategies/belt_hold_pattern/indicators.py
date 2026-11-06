"""Belt Hold indicators: EMA(20) trend context + ATR(14) + candle shape."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "ema20",
    "atr14",
    "candle_range",
    "body_frac",
    "open_low_frac",
    "open_high_frac",
    "upper_shadow_frac",
    "lower_shadow_frac",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema20"] = B.ema(df["c"], 20)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    rng = (df["h"] - df["l"]).replace(0, float("nan"))
    df["candle_range"] = df["h"] - df["l"]
    df["body_frac"] = (df["c"] - df["o"]).abs() / rng
    df["open_low_frac"] = (df["o"] - df["l"]) / rng
    df["open_high_frac"] = (df["h"] - df["o"]) / rng
    df["upper_shadow_frac"] = (df["h"] - df["c"].where(df["c"] > df["o"], df["o"])) / rng
    # Upper shadow = high - max(open, close); lower shadow = min(open, close) - low.
    hi_body = df[["o", "c"]].max(axis=1)
    lo_body = df[["o", "c"]].min(axis=1)
    df["upper_shadow_frac"] = (df["h"] - hi_body) / rng
    df["lower_shadow_frac"] = (lo_body - df["l"]) / rng
    return df
