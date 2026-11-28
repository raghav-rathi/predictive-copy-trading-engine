"""Balance Line pullback indicators (Bill Williams Profitunity).

    median   -- (h + l) / 2
    jaw      -- SMMA(median, 13), the Alligator's Jaw = the
                Balance Line
    teeth    -- SMMA(median, 8)
    lips     -- SMMA(median, 5)
    atr14    -- Wilder ATR(14) for the touch tolerance
    mouth_up -- lips > teeth > jaw (Alligator mouth open up)
    mouth_down -- lips < teeth < jaw (mouth open down)
    touch_long  -- bar low inside [jaw - 0.5*ATR, jaw + 0.5*ATR]
    touch_short -- bar high inside [jaw - 0.5*ATR, jaw + 0.5*ATR]
    touch_long_recent / touch_short_recent -- a touch within
                the last 5 bars (including the current bar)

SMMA[i] = (SMMA[i-1]*(n-1) + price[i]) / n, seeded with the
simple average of the first n prices (first valid value at
index n-1) -- the same pattern as
strategies/alligator_awesome_combo/indicators.py.

DEVIATION, documented: the book displaces the Alligator
lines 8/5/3 bars into the future for plotting. Those
shifted values are NOT used here -- UNSHIFTED SMMA values
only. Using the forward displacement in a live signal
would be lookahead (it needs future bars); the
displacement is a charting convention, not a trading rule.

No lookahead: SMMA/ATR are causal recursions; the touch
test and the 5-bar rolling window read only bars through
the current one.
"""

import numpy as np
import pandas as pd

from strategies import base as B

JAW_N = 13
TEETH_N = 8
LIPS_N = 5
ATR_N = 14
TOUCH_TOL = 0.5  # in ATR multiples
TOUCH_WINDOW = 5  # bars


def smma(s, n: int):
    """Wilder-smoothed moving average.

    SMMA[i] = (SMMA[i-1]*(n-1) + price[i]) / n, seeded with the
    simple average of the first n prices (first valid value at
    index n-1). NaN before that.
    """
    vals = s.to_numpy(float)
    out = np.full(len(vals), np.nan)
    if len(vals) >= n:
        out[n - 1] = vals[:n].mean()
        for i in range(n, len(vals)):
            out[i] = (out[i - 1] * (n - 1) + vals[i]) / n
    return pd.Series(out, index=s.index)


def add_indicators(
    df: pd.DataFrame,
    jaw_n: int = JAW_N,
    teeth_n: int = TEETH_N,
    lips_n: int = LIPS_N,
    atr_n: int = ATR_N,
    touch_tol: float = TOUCH_TOL,
    touch_window: int = TOUCH_WINDOW,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    df["median"] = median
    df["jaw"] = smma(median, jaw_n)
    df["teeth"] = smma(median, teeth_n)
    df["lips"] = smma(median, lips_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    df["mouth_up"] = (df["lips"] > df["teeth"]) & (df["teeth"] > df["jaw"])
    df["mouth_down"] = (df["lips"] < df["teeth"]) & (df["teeth"] < df["jaw"])
    tol = touch_tol * df["atr14"]
    df["touch_long"] = (df["l"] >= df["jaw"] - tol) & (df["l"] <= df["jaw"] + tol)
    df["touch_short"] = (df["h"] >= df["jaw"] - tol) & (df["h"] <= df["jaw"] + tol)
    df["touch_long_recent"] = (
        df["touch_long"].rolling(touch_window, min_periods=1).max() > 0
    )
    df["touch_short_recent"] = (
        df["touch_short"].rolling(touch_window, min_periods=1).max() > 0
    )
    return df
