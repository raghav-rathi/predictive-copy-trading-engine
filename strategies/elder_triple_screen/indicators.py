"""Triple Screen (Alexander Elder) indicators.

Screen 1 -- trend, factor-5 higher timeframe: 1h bars are resampled into
6h bars (o=first, h=max, l=min, c=last, v=sum) and a MACD(fast, slow,
signal) is computed on the 6h closes. The trend screen is the MACD
histogram:
    trend_up_6h   = (hist > 0) & (hist rising vs previous 6h bar)
    trend_down_6h = (hist < 0) & (hist falling vs previous 6h bar)

Resample map (NO LOOKAHEAD): a 1h bar with open time t sits in 6h bin
k = floor(t / 6h_ms). Bin k only completes at (k+1)*6h, so bar t may
read only bins that finished at or before t -- i.e. the most recent
completed bin, k-1. The 1h trend columns are therefore the 6h trend
shifted by one bin and ffilled onto the 1h index: every 1h bar reads
the trend of the last 6h bar that fully closed at or before its open.
Bars in the very first 6h block (no completed 6h bar yet) get False and
fall inside WARMUP anyway.

Screen 2 -- wave, 1h: Force Index fi = (c - c[1]) * v, smoothed to
EMA(2) (Elder's recommended short EMA for the hourly Force Index).
"""

import pandas as pd

from strategies import base as B

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
RESAMPLE_FACTOR = 5  # 1h -> 6h: the factor-5 higher timeframe
H6_MS = 6 * 3_600_000
ATR_LEN = 14


def _to_6h(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate 1h bars into completed 6h bins.

    Bin k covers [k*6h_ms, (k+1)*6h_ms) and is indexed by k. Bins with
    no bars (shouldn't happen on clean 1h data) simply don't appear.
    """
    bins = (df["t"] // H6_MS).astype("int64")
    return (
        df.assign(_bin=bins)
        .groupby("_bin", sort=True)
        .agg(
            o=("o", "first"),
            h=("h", "max"),
            l=("l", "min"),
            c=("c", "last"),
            v=("v", "sum"),
        )
    )


def add_indicators(
    df: pd.DataFrame,
    macd_fast: int = MACD_FAST,
    macd_slow: int = MACD_SLOW,
    macd_signal: int = MACD_SIGNAL,
) -> pd.DataFrame:
    df = df.copy()

    # --- Screen 1: 6h trend -------------------------------------------------
    h6 = _to_6h(df)
    hist = B.macd(h6["c"], macd_fast, macd_slow, macd_signal)["macd_hist"]
    up = (hist > 0) & (hist > hist.shift(1))
    dn = (hist < 0) & (hist < hist.shift(1))
    # shift(1): bar t reads only 6h bins completed at or before t.
    up_completed = pd.Series(up.shift(1).to_numpy(), index=up.index)
    dn_completed = pd.Series(dn.shift(1).to_numpy(), index=dn.index)
    bin_of_bar = (df["t"] // H6_MS).astype("int64")
    df["trend_up_6h"] = (
        bin_of_bar.map(up_completed).ffill().fillna(False).astype(bool)
    )
    df["trend_down_6h"] = (
        bin_of_bar.map(dn_completed).ffill().fillna(False).astype(bool)
    )
    df["macd_hist_6h"] = bin_of_bar.map(
        pd.Series(hist.shift(1).to_numpy(), index=hist.index)
    )

    # --- Screen 2: 1h wave ---------------------------------------------------
    df["fi"] = (df["c"] - df["c"].shift(1)) * df["v"]
    df["fi_ema2"] = B.ema(df["fi"], 2)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_LEN)
    return df
