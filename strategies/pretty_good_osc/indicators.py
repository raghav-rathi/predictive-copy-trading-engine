"""Pretty Good Oscillator indicators (Mark Johnson).

    PGO = (close - SMA(close, 14)) / SMA(ATR(14), 14)

The oscillator expresses how far the close has moved from its 14-bar
simple moving average, in units of the average true range over the
same 14 bars. It is dimensionless: |PGO| > 3 means the close sits more
than three average ranges from its mean — Johnson framed it for
breakout systems, where such a displacement marks a genuine thrust
rather than noise. The denominator is smoothed with its own 14-bar
SMA (not the raw ATR) so a single gap bar cannot collapse the ratio.

All series are causal (bar i uses only bars <= i); the harness
executes at bar i+1's open.
"""

import numpy as np
import pandas as pd

from strategies.base import atr, sma

PGO_N = 14


def add_indicators(df: pd.DataFrame, pgo_n: int = 14,
                   trigger: float = 3.0) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    atr14 = atr(df["h"], df["l"], df["c"], pgo_n)
    denom = sma(atr14, pgo_n)
    num = c - sma(c, pgo_n)
    # avoid division by zero: an ATR can never be <= 0 on real OHLC data,
    # but the synthetic edge case would produce inf; guard explicitly.
    pgo = np.where(
        denom.to_numpy() > 0,
        num.to_numpy() / np.where(denom.to_numpy() > 0, denom.to_numpy(), 1.0),
        0.0,
    )
    df["atr14"] = atr14
    df["atr14_sma"] = denom
    df["pgo"] = pgo
    df["pgo_trigger"] = trigger
    return df
