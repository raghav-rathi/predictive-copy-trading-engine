"""Fair Value Gap (ICT / Smart Money Concepts): the 3-candle imbalance, mechanized.

A bullish fair value gap is born at bar i when candle i closes leaving an
untraded band between candle i-2's high and candle i's low:

    l[i] > h[i-2]  AND  range(i-1) > 1.5 * ATR(14)[i-1]

The middle candle must be impulsive ("displacement"): its range exceeds
1.5x the ATR at its own close, so the gap was carved by aggressive order
flow rather than drift. Bearish mirror: h[i] < l[i-2] with the same
displacement filter. The gap is only knowable once bar i closes, so
detection at row i uses data through bar i only -- no lookahead.

Zone lifecycle: only the most recent unmitigated FVG per direction is
kept. A bullish zone [fvg_low = h[i-2], fvg_high = l[i]] dies on the
first bar whose low trades below fvg_low (l < fvg_low); a bearish zone
[fvg_low = h[i], fvg_high = l[i-2]] dies when h > fvg_high. Columns
fvg_bull_low/high and fvg_bear_low/high carry the active zone, NaN when
none is live (implemented as a simple forward loop; ~5k bars is cheap).

Columns:

    fvg_bull_low, fvg_bull_high -- active bullish gap zone (NaN if none)
    fvg_bear_low, fvg_bear_high -- active bearish gap zone (NaN if none)
    atr                          -- Wilder ATR(14), the displacement yardstick
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
DISPL_MULT = 1.5  # displacement threshold: mid-candle range vs ATR, fixed a priori


def _zones(h: np.ndarray, l: np.ndarray, atr: np.ndarray):
    """Forward-fill the active per-direction FVG zone (NaN when none).

    Detection at row i reads only l[i], h[i-2], the range of candle i-1
    and atr[i-1] -- everything known at bar i's close. A newborn zone can
    never self-mitigate on its own bar: bullish birth implies
    l[i] > h[i-2] = fvg_low, bearish birth implies h[i] < l[i-2] = fvg_high.
    """
    n = len(h)
    bull_low = np.full(n, np.nan)
    bull_high = np.full(n, np.nan)
    bear_low = np.full(n, np.nan)
    bear_high = np.full(n, np.nan)
    bull = (np.nan, np.nan)
    bear = (np.nan, np.nan)
    for i in range(2, n):
        atr_prev = atr[i - 1]
        if atr_prev == atr_prev:  # not NaN: ATR has spun up
            impulsive = (h[i - 1] - l[i - 1]) > DISPL_MULT * atr_prev
            if impulsive:
                if l[i] > h[i - 2]:  # bullish 3-candle gap
                    bull = (h[i - 2], l[i])
                if h[i] < l[i - 2]:  # bearish 3-candle gap (mutually exclusive)
                    bear = (h[i], l[i - 2])
        # mitigation: most recent unmitigated zone only
        if bull[0] == bull[0] and l[i] < bull[0]:
            bull = (np.nan, np.nan)
        if bear[0] == bear[0] and h[i] > bear[1]:
            bear = (np.nan, np.nan)
        bull_low[i], bull_high[i] = bull
        bear_low[i], bear_high[i] = bear
    return bull_low, bull_high, bear_low, bear_high


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    bull_low, bull_high, bear_low, bear_high = _zones(h, l, df["atr"].to_numpy(dtype=float))
    df["fvg_bull_low"] = bull_low
    df["fvg_bull_high"] = bull_high
    df["fvg_bear_low"] = bear_low
    df["fvg_bear_high"] = bear_high
    return df
