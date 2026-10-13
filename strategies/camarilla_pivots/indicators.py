"""Camarilla pivots (Nick Stott, 1989 bond-floor method).

Crypto trades 24/7, so a "session" is defined as a 24h UTC day (parameterizable
to a rolling-24h window for calibration). From the PRIOR session's H/L/C:

    R4 = C + (H-L) * 1.1 / 2      R3 = C + (H-L) * 1.1 / 4
    S3 = C - (H-L) * 1.1 / 4      S4 = C - (H-L) * 1.1 / 2
    mid = (R3 + S3) / 2  (pivot mid, fade target)

Pure pandas; no lookahead (prior-session stats only).
"""

import numpy as np
import pandas as pd

SESSION = "utc"  # or "rolling"


def add_indicators(df: pd.DataFrame, session: str = SESSION) -> pd.DataFrame:
    df = df.copy()
    df["sess"] = pd.to_datetime(df["t"], unit="ms", utc=True).dt.floor("D")
    if session == "utc":
        sess_stats = (
            df.groupby("sess")
            .agg(h=("h", "max"), l=("l", "min"), c=("c", "last"))
            .shift(1)
        )
        prior = df["sess"].map(sess_stats["h"]).astype(float)
        prior_l = df["sess"].map(sess_stats["l"]).astype(float)
        prior_c = df["sess"].map(sess_stats["c"]).astype(float)
    elif session == "rolling":
        n = 24
        prior = df["h"].rolling(n, min_periods=n).max().shift(1)
        prior_l = df["l"].rolling(n, min_periods=n).min().shift(1)
        prior_c = df["c"].shift(1)
    else:
        raise ValueError(f"bad session {session}")
    rng = prior - prior_l
    df["cam_R4"] = prior_c + rng * 1.1 / 2
    df["cam_R3"] = prior_c + rng * 1.1 / 4
    df["cam_S3"] = prior_c - rng * 1.1 / 4
    df["cam_S4"] = prior_c - rng * 1.1 / 2
    df["cam_mid"] = (df["cam_R3"] + df["cam_S3"]) / 2
    return df
