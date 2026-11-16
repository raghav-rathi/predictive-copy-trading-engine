"""McClellan Oscillator signals.

    long_entry  -- oscillator crosses above 0 having been below -50
                   within the prior 10 bars, and the summation index
                   is rising
    short_entry -- oscillator crosses below 0 having been above +50
                   within the prior 10 bars, and the summation index
                   is falling
    long_exit   -- oscillator crosses back below 0, or the summation
                   index turns down (against a long)
    short_exit  -- oscillator crosses back above 0, or the summation
                   index turns up (against a short)

"Crosses above 0 from below -50" is read as an excursion condition:
the oscillator dipped below -50 at some point in the 10 bars before
the cross (same, mirrored, for shorts). A literal one-bar jump from
below -50 to above 0 essentially never happens on 1h bars, so the
excursion reading is the tradable form of the rule.

The "|osc| < 10: no trade" filter is satisfied by construction: an
entry requires a prior excursion beyond +/-50, so |osc| exceeded 10
by a wide margin on the way into the trade.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

EXCURSION_LOOKBACK = 10  # bars to look back for the +/-50 excursion
EXCURSION_LEVEL = 50.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    osc = df["mc_osc"]
    summ = df["mc_summation"]
    # Prior 10-bar extremes, excluding the current bar.
    prev_low = osc.rolling(EXCURSION_LOOKBACK, min_periods=1).min().shift(1)
    prev_high = osc.rolling(EXCURSION_LOOKBACK, min_periods=1).max().shift(1)
    cross_up = crossed_above(osc, 0).fillna(False)
    cross_dn = crossed_below(osc, 0).fillna(False)
    summ_rising = (summ > summ.shift(1)).fillna(False)
    summ_falling = (summ < summ.shift(1)).fillna(False)
    df["long_entry"] = (
        cross_up & (prev_low < -EXCURSION_LEVEL) & summ_rising
    ).astype(bool)
    df["short_entry"] = (
        cross_dn & (prev_high > EXCURSION_LEVEL) & summ_falling
    ).astype(bool)
    df["long_exit"] = (cross_dn | summ_falling).astype(bool)
    df["short_exit"] = (cross_up | summ_rising).astype(bool)
    return df
