"""Ichimoku Kumo (cloud) breakout indicators (Goichi Hosoda;
Wikipedia, "Ichimoku Kinkō Hyō").

Uses strategies.base.ichimoku (tenkan 9, kijun 26, senkou 52):

    tenkan   = (highest high(9) + lowest low(9)) / 2
    kijun    = (highest high(26) + lowest low(26)) / 2
    senkou_a = (tenkan + kijun) / 2, shifted +26 bars
    senkou_b = (highest high(52) + lowest low(52)) / 2, shifted +26 bars

The cloud at bar i is the space between senkou_a and senkou_b.
Because both spans are shifted +26, the cloud value read at
bar i was computed from data through bar i-26 — it is known
at bar i and carries no lookahead.

The chikou span is DELIBERATELY NOT copied here: base.ichimoku
computes it as close shifted -26 (a lookahead), and this
strategy never reads it.

Columns:
    tenkan, kijun, senkou_a, senkou_b
    cloud_top    -- max(senkou_a, senkou_b)
    cloud_bottom -- min(senkou_a, senkou_b)

No lookahead: every value on bar j uses data through bar j
only (rolling extremes plus a +26 shift of already-known
values).
"""

import pandas as pd

from strategies import base as B

TENKAN = 9    # shipped default (Hosoda standard)
KIJUN = 26    # shipped default (Hosoda standard)
SENKOU = 52   # shipped default (Hosoda standard)


def add_indicators(
    df: pd.DataFrame,
    tenkan: int = TENKAN,
    kijun: int = KIJUN,
    senkou: int = SENKOU,
) -> pd.DataFrame:
    df = df.copy()
    ich = B.ichimoku(df["h"], df["l"], df["c"], tenkan, kijun, senkou)
    df["tenkan"] = ich["tenkan"]
    df["kijun"] = ich["kijun"]
    df["senkou_a"] = ich["senkou_a"]
    df["senkou_b"] = ich["senkou_b"]
    # NOTE: ich["chikou"] is never read — it is close shifted -26 (lookahead).
    df["cloud_top"] = pd.concat([df["senkou_a"], df["senkou_b"]], axis=1).max(axis=1)
    df["cloud_bottom"] = pd.concat([df["senkou_a"], df["senkou_b"]], axis=1).min(axis=1)
    return df
