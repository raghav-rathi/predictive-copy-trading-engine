"""Parabolic SAR(0.02, 0.20) flip gated by ADX(14) trend strength.

Long: PSAR flips from above price to below price AND ADX > 25
      AND +DI > -DI.
Short: PSAR flips from below to above AND ADX > 25 AND -DI > +DI.

PSAR is a hand-rolled Wilder PSAR (base.py has no PSAR helper)
implemented as a causal forward loop — see parabolic_sar() below.
ADX/+DI/-DI via strategies.base.adx.

Columns:
    psar     -- Wilder Parabolic SAR
    adx      -- Wilder ADX(14)
    plus_di  -- +DI(14)
    minus_di -- -DI(14)
    atr      -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

PSAR_STEP = 0.02
PSAR_MAX_AF = 0.20
ADX_PERIOD = 14

INDICATOR_COLS = ["psar", "adx", "plus_di", "minus_di", "atr"]

def parabolic_sar(h, l, c, step=0.02, max_af=0.20):
    """Wilder Parabolic SAR, causal forward loop.

    Initial trend is long with SAR = low[0] and EP = high[0] (uses
    only bar 0, so no lookahead). On each later bar the SAR is
    extrapolated from the prior SAR/EP, clamped so it never goes
    above the lows of the prior two bars in an uptrend (below the
    highs of the prior two bars in a downtrend), then a flip is
    checked against the current bar's low/high: if price touches
    the SAR the trend flips and the SAR on the flip bar becomes
    the prior extreme point. AF starts at `step` and rises by
    `step` per new extreme, capped at `max_af`.
    """
    import numpy as np
    import pandas as pd

    h_v = h.to_numpy(dtype=float)
    l_v = l.to_numpy(dtype=float)
    c_v = c.to_numpy(dtype=float)
    n = len(c_v)
    sar = np.full(n, np.nan)
    if n == 0:
        return pd.Series(sar, index=c.index, name="psar")
    # Initial trend: long, SAR at the first bar's low.
    up = True
    ep = h_v[0]
    af = step
    sar[0] = l_v[0]
    for i in range(1, n):
        prev = sar[i - 1]
        if up:
            s = prev + af * (ep - prev)
            # Never above the lows of the prior two bars.
            cap = l_v[i - 1]
            if i >= 2:
                cap = min(cap, l_v[i - 2])
            s = min(s, cap)
            if l_v[i] < s:
                # Flip to downtrend; SAR is the prior extreme high.
                up = False
                sar[i] = ep
                ep = l_v[i]
                af = step
            else:
                sar[i] = s
                if h_v[i] > ep:
                    ep = h_v[i]
                    af = min(af + step, max_af)
        else:
            s = prev + af * (ep - prev)
            floor = h_v[i - 1]
            if i >= 2:
                floor = max(floor, h_v[i - 2])
            s = max(s, floor)
            if h_v[i] > s:
                up = True
                sar[i] = ep
                ep = h_v[i]
                af = step
            else:
                sar[i] = s
                if l_v[i] < ep:
                    ep = l_v[i]
                    af = min(af + step, max_af)
    return pd.Series(sar, index=c.index, name="psar")


def add_indicators(df: pd.DataFrame, step: float = PSAR_STEP,
                   max_af: float = PSAR_MAX_AF,
                   adx_n: int = ADX_PERIOD) -> pd.DataFrame:
    df = df.copy()
    df["psar"] = parabolic_sar(df["h"], df["l"], df["c"], step, max_af)
    adx_df = B.adx(df["h"], df["l"], df["c"], adx_n)
    df["adx"] = adx_df["adx"]
    df["plus_di"] = adx_df["plus_di"]
    df["minus_di"] = adx_df["minus_di"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
