"""Fakey (false break of an inside bar) indicators.

Nial Fuller's Fakey is a three-bar pattern:

    mother bar  i-2 -- the range that contains the setup
    inside bar  i-1 -- high < mother high AND low > mother low
    break bar   i   -- pokes outside the inside bar, then closes
                       back inside the mother bar's range

The false break traps breakout traders on the wrong side; the
close back inside the mother bar is the tell that the break was
fake, and the trade runs in the direction of the failed break.

This module flags the inside-bar structure. The break/close
conditions live in signals.py, where the confirmation mode
(mother-bar range vs inside-bar range) is a parameter.

Columns:
    is_inside  -- bar i is an inside bar relative to bar i-1
                  (high[i] < high[i-1] AND low[i] > low[i-1])

No lookahead: the value on bar i uses data through bar i's close
only (all comparisons are to prior bars).
"""

import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_inside"] = ((df["h"] < df["h"].shift(1)) & (df["l"] > df["l"].shift(1))).fillna(False).astype(bool)
    return df
