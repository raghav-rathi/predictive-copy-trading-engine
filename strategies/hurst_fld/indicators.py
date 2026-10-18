"""J.M. Hurst's Future Lines of Demarcation (FLD) indicators.

Hurst's FLD(N) at bar i is the N-bar cycle's midline drawn ahead of price:
FLD(N)[i] = median(h,l)[i - N/2]. Plotting the midline shifted back by N/2
turns the symmetric moving average into a leading/confirmatory line: price
crossing the FLD signals the cycle turn that the midline centered at i
already "saw". No lookahead here: comparing close[i] to median[i - N/2]
uses only data through bar i.

We track three FLDs: FLD(20), FLD(40), FLD(80) (shift 10 / 20 / 40).
A bullish cascade (price above FLD20 above FLD40 above FLD80) means the
20-, 40- and 80-bar cycles are all aligned upward; the mirror applies
for bearish. Source: J.M. Hurst, *The Profit Magic of Stock Transaction
Timing*; methodology at https://notes.hurstcycles.com/from-analysis-to-trading/
"""

import pandas as pd

from strategies import base as B

FLD_PERIODS = (20, 40, 80)


def _fld(median: pd.Series, n: int) -> pd.Series:
    """FLD(N) = median shifted back by N/2 bars. Past data only."""
    return median.shift(n // 2).rename(f"fld_{n}")


def add_indicators(
    df: pd.DataFrame,
    periods: tuple[int, ...] = FLD_PERIODS,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    df["median"] = median
    for n in periods:
        df[f"fld_{n}"] = _fld(median, n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
