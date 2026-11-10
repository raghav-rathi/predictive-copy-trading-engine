"""Tushar Chande's Intraday Momentum Index (IMI).

Published formula (Chande, "The New Technical Trader"; see also
https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/intraday_momentum_index):

  per bar:  gain = max(close - open, 0);  loss = max(open - close, 0)
  IMI = 100 * sum(gains over last 14 bars)
            / (sum(gains) + sum(losses))

  If sum(gains) + sum(losses) == 0 (no intraday movement at all in the
  window), IMI = 50.

Unlike RSI, IMI uses open-to-close movement inside each bar, not
close-to-close changes, so it measures intraday (within-bar) momentum.
IMI is bounded [0, 100]. All columns are causal: the value on bar i
uses only bars 0..i.
"""

import numpy as np
import pandas as pd

IMI_PERIOD = 14

INDICATOR_COLS = ["imi"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    gain = (df["c"] - df["o"]).clip(lower=0)
    loss = (df["o"] - df["c"]).clip(lower=0)
    gain_sum = gain.rolling(IMI_PERIOD, min_periods=IMI_PERIOD).sum()
    loss_sum = loss.rolling(IMI_PERIOD, min_periods=IMI_PERIOD).sum()
    total = gain_sum + loss_sum
    imi = 100.0 * gain_sum / total
    # Zero total movement over a complete window -> neutral 50, not NaN.
    # (total is NaN for the first IMI_PERIOD - 1 bars, and NaN == 0 is
    # False, so the warmup bars correctly stay NaN.)
    imi = imi.mask(total == 0, 50.0)
    df["imi"] = imi
    return df
