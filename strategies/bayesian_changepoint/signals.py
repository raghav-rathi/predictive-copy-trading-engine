"""Bayesian changepoint signals.

    long_entry  = changepoint detected (P(change) > 0.5) and the
                  post-change mean return is positive
    short_entry = changepoint detected and the post-change mean
                  return is negative

Exits: the next changepoint, or the post-change mean flips sign
against the position. (The harness checks exits before entries each
bar and only exits an open position, so a changepoint bar that is
also an entry bar cannot immediately exit the trade it opens.)

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    df = df.copy()
    cp = df["bocd_p_change"] > threshold
    mean = df["bocd_post_mean"]
    df["long_entry"] = (cp & (mean > 0)).fillna(False).astype(bool)
    df["short_entry"] = (cp & (mean < 0)).fillna(False).astype(bool)
    df["long_exit"] = (cp | (mean < 0)).fillna(False).astype(bool)
    df["short_exit"] = (cp | (mean > 0)).fillna(False).astype(bool)
    return df
