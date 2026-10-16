"""Key-reversal signals.

  long_entry:  a (volume-confirmed) bullish key reversal completes at
               bar i's close; the harness executes it at bar i+1's open.
  short_entry: mirror on bearish key reversals.
  long_exit:   a bearish key reversal while long (pattern reversal).
  short_exit:  a bullish key reversal while short.

USE_VOLUME_FILTER selects the shipped variant. Calibration sweeps
True/False and the winner is set here.
"""

import pandas as pd

USE_VOLUME_FILTER = False  # shipped: calibration tested the 1.5x volume
# filter and dropped it — the unfiltered 20-bar variant wins on BTC/ETH/HYPE


def add_signals(df: pd.DataFrame,
                use_volume_filter: bool = USE_VOLUME_FILTER) -> pd.DataFrame:
    df = df.copy()
    if use_volume_filter:
        bull = df["kr_bull"] & df["kr_vol_conf"]
        bear = df["kr_bear"] & df["kr_vol_conf"]
    else:
        bull = df["kr_bull"]
        bear = df["kr_bear"]
    df["long_entry"] = bull.fillna(False).astype(bool)
    df["short_entry"] = bear.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
