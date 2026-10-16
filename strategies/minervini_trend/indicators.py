"""Minervini Trend Template indicators.

Mark Minervini's stage-analysis "Trend Template" (from *Trade Like a Stock
Market Wizard*, 2013) expressed in my own implementation. On 1h bars one
trading day = 24 bars, so the daily windows become:

  50d  -> 1200 bars     150d -> 3600 bars     200d -> 4800 bars
  30d  ->  720 bars      52wk -> 12480 bars (per the published template)

The full template (ALL must hold; RS-rating criterion omitted — it needs
a market benchmark, documented in CALIBRATION.md):

  1. c  > SMA(150d) and c > SMA(200d)          -- price above the big MAs
  2. SMA(150d) > SMA(200d)                    -- 150d above 200d
  3. SMA(200d) > SMA(200d)[30d ago]           -- 200d rising vs a month ago
  4. SMA(50d) > SMA(150d) and > SMA(200d)     -- 50d leads both
  5. c > SMA(50d)                             -- price above 50d
  6. c >= 1.30 * 12480-bar lowest low         -- >= 30% above the 52wk low
  7. c >= 0.75 * 12480-bar highest high       -- within 25% of the 52wk high

Approximation note: the backtest data is only ~5,158 hourly bars, shorter
than the 12480-bar and 4800-bar windows. Rolling windows use
min_periods=1 so the template is computable over the whole series; on
short history the "52wk" high/low simply uses all available history (the
standard treatment for a newly-listed asset). No lookahead: every term
uses data through bar i's close only.
"""

import pandas as pd

DAY = 24
SMA50 = 50 * DAY      # 1200
SMA150 = 150 * DAY    # 3600
SMA200 = 200 * DAY    # 4800
RISE_LAG = 30 * DAY   # 720
YEAR_WIN = 12480      # published 52wk window in hourly bars

LOW52_MULT = 1.30     # >= 30% above the 52wk low
HIGH52_MULT = 0.75    # within 25% of the 52wk high


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]
    sma50 = c.rolling(SMA50, min_periods=1).mean()
    sma150 = c.rolling(SMA150, min_periods=1).mean()
    sma200 = c.rolling(SMA200, min_periods=1).mean()
    rising200 = sma200 > sma200.shift(RISE_LAG)
    lo_year = l.rolling(YEAR_WIN, min_periods=1).min()
    hi_year = h.rolling(YEAR_WIN, min_periods=1).max()

    df["mt_sma50"] = sma50
    df["mt_sma150"] = sma150
    df["mt_sma200"] = sma200
    df["mt_lo_year"] = lo_year
    df["mt_hi_year"] = hi_year
    df["mt_template"] = (
        (c > sma150)
        & (c > sma200)
        & (sma150 > sma200)
        & rising200
        & (sma50 > sma150)
        & (sma50 > sma200)
        & (c > sma50)
        & (c >= LOW52_MULT * lo_year)
        & (c >= HIGH52_MULT * hi_year)
    )
    return df
