"""ICT inducement -> sweep -> MSS -> OTE signals.

Entry only: long on a bullish OTE-entry bar (ict_dir == +1), short
on a bearish one (ict_dir == -1). The full sequence — inducement,
sweep into the POI, market-structure shift, displacement with a
fair-value gap, retracement to the 70.5% OTE level — is detected in
indicators.py; signals.py is a pure mapping.

No signal-level exits: trade management is the harness stop (beyond
the POI, approximated by 2xATR — see CALIBRATION.md), the 2R target
(4xATR) and the 72-bar max hold. The harness executes entries at
the next bar's open, so the fill lands just after the OTE touch bar.

Signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    direction = df["ict_dir"].fillna(0).to_numpy(dtype=int)
    df["long_entry"] = direction == 1
    df["short_entry"] = direction == -1
    df["long_exit"] = np.zeros(len(df), dtype=bool)
    df["short_exit"] = np.zeros(len(df), dtype=bool)
    return df
