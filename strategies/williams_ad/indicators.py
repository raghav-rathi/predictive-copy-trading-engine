"""Larry Williams Accumulation/Distribution (WAD) indicators.

WAD is a cumulative series that adds buying/selling pressure each bar:
    pc  = previous close
    TRL = min(pc, low)      -- true range low
    TRH = max(pc, high)     -- true range high
    if close > pc: WAD += (close - TRL)   (accumulation)
    elif close < pc: WAD += (close - TRH) (distribution)
    else: WAD unchanged

Then a 20-bar SMA of WAD and a 50-bar SMA of price act as the trend
filters for the signal layer.

Source: cTrader built-in indicator docs (Larry Williams A/D).
No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WAD_SMA_N = 20
PRICE_SMA_N = 50


def add_indicators(
    df: pd.DataFrame,
    wad_sma_n: int = WAD_SMA_N,
    price_sma_n: int = PRICE_SMA_N,
) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]
    pc = c.shift(1)
    trl = pd.concat([pc, l], axis=1).min(axis=1)
    trh = pd.concat([pc, h], axis=1).max(axis=1)
    up = c > pc
    dn = c < pc
    inc = pd.Series(
        np.where(up.to_numpy(), (c - trl).to_numpy(),
                 np.where(dn.to_numpy(), (c - trh).to_numpy(), 0.0)),
        index=df.index,
    )
    # bar 0 has no previous close: no pressure added
    inc = inc.where(pc.notna(), 0.0)
    df["wad"] = inc.cumsum()
    df["wad_sma20"] = B.sma(df["wad"], wad_sma_n)
    df["price_sma50"] = B.sma(c, price_sma_n)
    df["atr"] = B.atr(h, l, c, 14)
    return df
