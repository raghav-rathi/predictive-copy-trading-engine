"""Polarized Fractal Efficiency signals (Hannula's usage).

Buy on the reversal from a minimum back toward zero; close when the
reading reaches its peak above zero (mirror image for shorts):

  long_entry:  PFE crosses above 0 AND min PFE over the last 20 bars < -30
  short_entry: PFE crosses below 0 AND max PFE over the last 20 bars > +30
  long_exit:   PFE crosses below +50 after having exceeded +50 at any
               point since entry (peak-reached exit) OR PFE crosses below 0
  short_exit:  PFE crosses above -50 after having been below -50 at any
               point since entry OR PFE crosses above 0

The peak tracking is a simple stateful scan over the signal frame:
an entry signal (re)arms the peak flag, and the flag is set while the
tracked position is open. This is causal -- the scan at bar i uses only
PFE values through bar i. Note the harness executes an entry signal at
bar i+1's open, so the scan tracks the peak from the entry-signal bar,
one bar before the actual fill; see CALIBRATION.md.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below

LOOKBACK_BARS = 20
EXTREME = 30.0
PEAK_LEVEL = 50.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pfe = df["pfe"]

    cross_up_zero = crossed_above(pfe, 0.0).fillna(False)
    cross_down_zero = crossed_below(pfe, 0.0).fillna(False)
    cross_down_peak = crossed_below(pfe, PEAK_LEVEL).fillna(False)
    cross_up_neg_peak = crossed_above(pfe, -PEAK_LEVEL).fillna(False)

    rolling_min = pfe.rolling(LOOKBACK_BARS, min_periods=LOOKBACK_BARS).min()
    rolling_max = pfe.rolling(LOOKBACK_BARS, min_periods=LOOKBACK_BARS).max()

    long_entry = (cross_up_zero & (rolling_min < -EXTREME)).fillna(False).astype(bool)
    short_entry = (cross_down_zero & (rolling_max > EXTREME)).fillna(False).astype(bool)

    # Stateful peak-reached exit scan (causal, bar i only sees data <= i).
    pfe_v = pfe.to_numpy(dtype=float)
    le_v = long_entry.to_numpy(dtype=bool)
    se_v = short_entry.to_numpy(dtype=bool)
    cdz_v = cross_down_zero.to_numpy(dtype=bool)
    cuz_v = cross_up_zero.to_numpy(dtype=bool)
    cdp_v = cross_down_peak.to_numpy(dtype=bool)
    cunp_v = cross_up_neg_peak.to_numpy(dtype=bool)
    n = len(df)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)

    in_long = False
    long_peak = False
    in_short = False
    short_peak = False
    for i in range(n):
        # Entries (re)arm the peak flag for a fresh position.
        if le_v[i]:
            in_long = True
            long_peak = False
        if se_v[i]:
            in_short = True
            short_peak = False
        if in_long:
            if np.isfinite(pfe_v[i]) and pfe_v[i] > PEAK_LEVEL:
                long_peak = True
            if (long_peak and cdp_v[i]) or cdz_v[i]:
                long_exit[i] = True
                in_long = False
                long_peak = False
        if in_short:
            if np.isfinite(pfe_v[i]) and pfe_v[i] < -PEAK_LEVEL:
                short_peak = True
            if (short_peak and cunp_v[i]) or cuz_v[i]:
                short_exit[i] = True
                in_short = False
                short_peak = False

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
