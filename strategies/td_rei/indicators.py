"""DeMark Range Expansion Index (TD REI) indicators.

Formula (Tom DeMark, "The New Science of Technical Analysis" (1994),
ch. 4; as documented in the AmiBroker AFL Formula Library and the
Wickra TD REI reference):

    high_mom_t = H_t - H_{t-2}
    low_mom_t  = L_t - L_{t-2}

    gate A: (H_t >= L_{t-5} or H_t >= L_{t-6})
            and (L_t <= H_{t-5} or L_t <= H_{t-6})
    gate B: (H_{t-2} >= C_{t-7} or H_{t-2} >= C_{t-8})
            and (L_{t-2} <= C_{t-7} or L_{t-2} <= C_{t-8})
    num_t = high_mom_t + low_mom_t   if (gate A or gate B), else 0
    den_t = |high_mom_t| + |low_mom_t|   (every bar, gated or not)

    REI_t = 100 * sum(num, 5) / sum(den, 5)
    (NaN while the 5-bar sums are not yet full, and NaN when
    sum(den, 5) == 0, i.e. no high/low movement at all.)

By construction |sum(num, 5)| <= sum(den, 5), so REI is bounded to
[-100, +100]: +100 when every bar in the window moved up, -100 when
every bar moved down, 0 when the moves cancel or the gate zeroes the
numerator. The gate only zeroes the numerator: a bar whose range does
not overlap the bars 5-6 back (and whose bar-two-back does not overlap
the closes 7-8 back) still adds its absolute move to the denominator,
pulling REI toward zero.

Note on the brief's "8-bar window": DeMark's canonical summation
window is 5 bars; 8 bars is the data lookback the gate needs (it
references closes 7-8 bars back). The 5-bar sum is implemented here,
per the published formula; see CALIBRATION.md for the correction note.
All shifts/rolling sums use data through bar i only: no lookahead.
"""

import numpy as np
import pandas as pd

REI_PERIOD = 5

INDICATOR_COLS = [
    "rei",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]
    high_mom = h - h.shift(2)
    low_mom = l - l.shift(2)

    gate_a = (
        ((h >= l.shift(5)) | (h >= l.shift(6)))
        & ((l <= h.shift(5)) | (l <= h.shift(6)))
    )
    gate_b = (
        ((h.shift(2) >= c.shift(7)) | (h.shift(2) >= c.shift(8)))
        & ((l.shift(2) <= c.shift(7)) | (l.shift(2) <= c.shift(8)))
    )
    gate = (gate_a | gate_b).fillna(False)

    num = (high_mom + low_mom).where(gate, 0.0)
    den = high_mom.abs() + low_mom.abs()
    # Bars before t-2 have no momentum at all: keep them NaN so the
    # 5-bar sums only become valid once 5 real bars exist.
    num = num.where(high_mom.notna())
    den = den.where(high_mom.notna())

    num_sum = num.rolling(REI_PERIOD, min_periods=REI_PERIOD).sum()
    den_sum = den.rolling(REI_PERIOD, min_periods=REI_PERIOD).sum()
    rei = 100.0 * num_sum / den_sum.replace(0, np.nan)
    df["rei"] = rei.clip(-100.0, 100.0)
    return df
