"""Bollinger Bandwidth expansion breakout.

bbw = (upper - lower) / mid for BB(20, 2). The signal is NOT the
squeeze (that is bollinger_squeeze, BB inside Keltner) and NOT the
first-close-outside rule (bollinger_band_walk): it requires the band
to be *expanding* (bbw above its own 20-bar SMA) at the breakout
close, i.e. volatility confirming the move. Columns: bb_upper,
bb_lower, bb_mid, bbw, bbw_ma, atr.
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], 20, 2.0)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bbw"] = (bb["bb_upper"] - bb["bb_lower"]) / bb["bb_mid"].replace(0, float("nan"))
    df["bbw_ma"] = df["bbw"].rolling(20, min_periods=20).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
