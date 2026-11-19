"""ATR-percentile volatility regime indicators.

ATR(14) percentile rank over the trailing 100 bars: the fraction
of the last 100 ATR values (including the current bar) less than
or equal to the current ATR. Above 0.60 is expansion, below 0.40
is compression, 0.40-0.60 is the middle regime (no entries).

Donchian(20) channel levels are taken EXCLUDING the current bar:
prev_high / prev_low are the 20-bar high/low as of the previous
bar's close (the rolling Donchian level shifted by one). A close
can never break a high that already includes its own bar, so the
exclusion is load-bearing for the breakout rule. Bollinger(20, 2)
supplies the fade levels in compression.

Columns:
    atr              -- Wilder ATR(14)
    atr_pct          -- ATR percentile rank over trailing 100 bars
    donchian_high_20 / donchian_low_20 -- rolling 20-bar channel
    prev_high / prev_low -- Donchian levels excluding the current bar
    donchian_mid     -- (prev_high + prev_low) / 2
    bb_mid / bb_upper / bb_lower -- Bollinger(20, 2) of close

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

ATR_WINDOW = 14
PCT_WINDOW = 100
EXPANSION_PCT = 0.60
COMPRESSION_PCT = 0.40
DONCHIAN_N = 20
BB_N = 20
BB_K = 2.0

INDICATOR_COLS = ["atr", "atr_pct", "prev_high", "prev_low",
                  "donchian_mid", "bb_mid", "bb_upper", "bb_lower"]


def _pct_rank_last(x):
    """Fraction of the window <= the last (current) value."""
    last = x[-1]
    return float((x <= last).mean())


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_WINDOW)
    df["atr_pct"] = df["atr"].rolling(PCT_WINDOW, min_periods=PCT_WINDOW).apply(
        _pct_rank_last, raw=True
    )

    don = B.donchian(df["h"], df["l"], DONCHIAN_N)
    df["donchian_high_20"] = don["donchian_high_20"]
    df["donchian_low_20"] = don["donchian_low_20"]
    # Prior 20-bar high/low EXCLUDING the current bar: the Donchian
    # level as of the previous bar's close.
    df["prev_high"] = df["donchian_high_20"].shift(1)
    df["prev_low"] = df["donchian_low_20"].shift(1)
    df["donchian_mid"] = (df["prev_high"] + df["prev_low"]) / 2

    bb = B.bollinger(df["c"], BB_N, BB_K)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    return df
