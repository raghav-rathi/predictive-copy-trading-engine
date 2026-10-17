"""Raschke Momentum Pinball indicators (Street Smarts, Connors & Raschke).

LBR/RSI = 3-period Wilder RSI of the 1-period rate-of-change of close
(the "momentum" series). No long-term directional meaning: it defines
"buy days" (pinball < 30) vs "sell days" (pinball > 70) for 1-3 bar flips.
All causal: only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

RSI_N = 3  # LBR/RSI period per the book
BUY_DAY = 30.0
SELL_DAY = 70.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mom = df["c"].diff()  # 1-period ROC of close = "momentum"
    df["pinball"] = B.rsi(mom, RSI_N)
    df["pinball_prev"] = df["pinball"].shift(1)
    return df
