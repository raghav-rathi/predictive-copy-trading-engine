"""Ulcer Index -- Peter Martin's downside-volatility gauge (1987).

    pctdd[j] = 100 * (close[j] - max(close[j-n+1..j])) / max(close[j-n+1..j])
    ulcer[j] = sqrt(mean(pctdd[j-n+1..j]^2))

The Ulcer Index measures only downside volatility: percent drawdown
from the trailing n-bar peak, root-mean-squared. A rising series has
UI == 0; a sharp drop makes it spike. That asymmetry is why it works
as a *regime gate for longs only*: trade breakouts when the gauge
reads calm (ulcer < 5), stand aside when it reads stressed, and treat
a panic spike (ulcer > 10) as a hard exit.

Columns:

    ulcer          -- UI(n) of close
    donchian_high_20 -- 20-bar rolling max of h (entry breakout level)
    donchian_low_20  -- 20-bar rolling min of l (kept for reference)
    donchian_low_10  -- 10-bar rolling min of l (exit level)
    atr            -- Wilder ATR(14) for the risk layer

No lookahead: the rolling max/min and the squared mean at bar j use
data through bar j only (min_periods=n). Entry crosses are taken
against the *shifted* Donchian level in signals.py.
"""

import numpy as np
import pandas as pd

from strategies import base as B

UI_N = 14       # shipped default (fixed a priori)
ENTRY_N = 20    # Donchian entry lookback
EXIT_N = 10     # Donchian exit lookback


def ulcer(c: pd.Series, n: int = UI_N) -> pd.Series:
    """Ulcer Index of the close series: sqrt(mean(pct-drawdown^2)) over n."""
    peak = c.rolling(n, min_periods=n).max()
    pctdd = 100.0 * (c - peak) / peak
    return np.sqrt((pctdd ** 2).rolling(n, min_periods=n).mean()).rename("ulcer")


def add_indicators(df: pd.DataFrame, n: int = UI_N,
                   entry_n: int = ENTRY_N,
                   exit_n: int = EXIT_N) -> pd.DataFrame:
    df = df.copy()
    df["ulcer"] = ulcer(df["c"], n)
    don_e = B.donchian(df["h"], df["l"], entry_n)
    df[f"donchian_high_{entry_n}"] = don_e[f"donchian_high_{entry_n}"]
    df[f"donchian_low_{entry_n}"] = don_e[f"donchian_low_{entry_n}"]
    don_x = B.donchian(df["h"], df["l"], exit_n)
    df[f"donchian_low_{exit_n}"] = don_x[f"donchian_low_{exit_n}"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
