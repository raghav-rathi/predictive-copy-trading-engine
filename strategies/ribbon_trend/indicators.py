"""EMA ribbon indicators (multi-EMA alignment trend system).

Ribbon = EMAs(8, 13, 21, 34, 55). Aligned bull: e8 > e13 > e21 > e34 > e55
(stacked and fanned). Aligned bear: the mirror. Fan spread = (e8 - e55) /
e55: a wide fan means a mature, healthy trend; a compressing fan (spread
shrinking through MIN_FAN) warns of exhaustion. Entries on alignment
flips; the fan filter keeps entries out of flat, tangled ribbons.
All causal.
"""

import pandas as pd

from strategies import base as B

LENS = (8, 13, 21, 34, 55)
MIN_FAN = 0.004  # 0.4% fan spread required to take an alignment flip


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    emas = [B.ema(df["c"], n) for n in LENS]
    for n, e in zip(LENS, emas):
        df[f"ribbon_e{n}"] = e
    e8, e13, e21, e34, e55 = emas
    bull = (e8 > e13) & (e13 > e21) & (e21 > e34) & (e34 > e55)
    bear = (e8 < e13) & (e13 < e21) & (e21 < e34) & (e34 < e55)
    df["ribbon_bull"] = bull.fillna(False)
    df["ribbon_bear"] = bear.fillna(False)
    df["ribbon_fan"] = ((e8 - e55) / e55.replace(0, float("nan"))).abs()
    return df
