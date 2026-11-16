"""ARMS Index / TRIN signals.

    long_entry  -- 10-bar TRIN crosses below 0.7 after having been
                   above 1.0 within the prior 10 bars (panic washout:
                   heavy volume into down bars, then the flow flips)
    short_entry -- TRIN crosses above 1.5 after having been below 1.0
                   within the prior 10 bars
    long_exit / short_exit -- TRIN reverts into the 0.9-1.1 band

"After being above 1.0" is read as an excursion condition: TRIN
exceeded 1.0 at some point in the 10 bars before the cross. A
literal one-bar jump from above 1.0 to below 0.7 is rare on 1h bars,
so the excursion reading is the tradable form of the rule.

No trade if either 10-bar volume sum is 0 (no volume on one side
makes the ratio meaningless). Max hold is enforced by the risk
config (24 bars).

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

EXCURSION_LOOKBACK = 10  # bars to look back for the 1.0 excursion
LONG_LEVEL = 0.7
SHORT_LEVEL = 1.5
BAND_LOW = 0.9
BAND_HIGH = 1.1


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    trin = df["trin"]
    prev_high = trin.rolling(EXCURSION_LOOKBACK, min_periods=1).max().shift(1)
    prev_low = trin.rolling(EXCURSION_LOOKBACK, min_periods=1).min().shift(1)
    cross_dn = crossed_below(trin, LONG_LEVEL).fillna(False)
    cross_up = crossed_above(trin, SHORT_LEVEL).fillna(False)
    has_volume = (df["trin_up_vol"] > 0) & (df["trin_dn_vol"] > 0)
    has_volume = has_volume.fillna(False)
    df["long_entry"] = (
        cross_dn & (prev_high > 1.0) & has_volume
    ).astype(bool)
    df["short_entry"] = (
        cross_up & (prev_low < 1.0) & has_volume
    ).astype(bool)
    in_band = ((trin >= BAND_LOW) & (trin <= BAND_HIGH)).fillna(False)
    df["long_exit"] = in_band.astype(bool)
    df["short_exit"] = in_band.astype(bool)
    return df
