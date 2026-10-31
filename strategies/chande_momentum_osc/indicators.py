"""Chande Momentum Oscillator (14).

CMO(14) = 100 * (UpSum - DnSum) / (UpSum + DnSum), where UpSum is the
sum of positive close-to-close changes over 14 bars and DnSum is the
sum of absolute negative close-to-close changes over the same window.
A window with no price movement at all (UpSum + DnSum == 0) yields
CMO = 0, not NaN. CMO ranges from -100 to +100 and, unlike RSI, uses
raw gain/loss sums rather than averages. All columns are causal.

Columns:
    cmo     -- Chande Momentum Oscillator (NaN until 14 changes exist)
    atr     -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

CMO_PERIOD = 14
OVERBOUGHT = 50.0
OVERSOLD = -50.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    delta = df["c"].diff()
    up = delta.clip(lower=0)
    dn = -delta.clip(upper=0)
    up_sum = up.rolling(CMO_PERIOD, min_periods=CMO_PERIOD).sum()
    dn_sum = dn.rolling(CMO_PERIOD, min_periods=CMO_PERIOD).sum()
    total = up_sum + dn_sum
    cmo = 100 * (up_sum - dn_sum) / total.replace(0, np.nan)
    cmo = cmo.where(total > 0, 0.0)
    df["cmo"] = cmo
    from strategies import base as B

    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
