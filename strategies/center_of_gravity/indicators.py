"""John Ehlers Center of Gravity indicators.

Over a trailing 10-bar window of closes p[0..9] (p[0] oldest):

    CG = -sum((i+1) * p[i] for i in 0..9) / sum(p[i])

Trigger = SMA(3) of CG.

Columns:
    cg -- Center of Gravity
    cg_trigger -- 3-bar SMA of CG
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. The weighted sum is computed as sum over j=0..9 of
(10-j) * close[t-j], which is the same sum with the newest bar
weighted 10 and the oldest weighted 1.

NOTE on convention: the brief's formula weights the MOST RECENT
price most heavily (weight 10) and the oldest least (weight 1),
with an overall negative sign. Ehlers' original paper weights the
opposite way (most recent price weight 1, oldest weight 10) and
inverts the sign so the oscillator moves in phase with price. The
implementation here follows the brief exactly; see CALIBRATION.md.
Also, no +(Length+1)/2 centering term is added (some platforms add
one so CG oscillates about zero); CG here sits near -5.5 on flat
prices, and only CG-vs-trigger crosses are traded.
"""

import pandas as pd

from strategies import base as B

CG_N = 10
TRIGGER_N = 3
ATR_N = 14


def add_indicators(df: pd.DataFrame, cg_n: int = CG_N,
                   trigger_n: int = TRIGGER_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    h = df["h"]
    l = df["l"]

    # Weighted sum: newest bar (j=0) weight cg_n, oldest (j=cg_n-1)
    # weight 1. NaN until cg_n bars exist (shift introduces NaN).
    weighted = sum((cg_n - j) * c.shift(j) for j in range(cg_n))
    total = c.rolling(cg_n, min_periods=cg_n).sum()
    df["cg"] = -weighted / total
    df["cg_trigger"] = df["cg"].rolling(trigger_n, min_periods=trigger_n).mean()
    df["atr"] = B.atr(h, l, c, atr_n)
    return df
