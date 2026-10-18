"""George Douglass Taylor's 3-day Book Method indicators.

Taylor (*The Taylor Trading Technique*, 1950) ran a rolling 3-day rhythm:
Buy Day -> Sell Day -> Sell-Short Day -> Buy Day ..., anchored to the NY
trading day. Implementation here:

* Cycle days run on NY time (EDT = UTC-4, assumed fixed for the whole
  window -- the Mar->Oct sample sits entirely inside US daylight time).
  The cycle is anchored at Monday 2026-01-05 00:00 NY; each NY day gets a
  label (day_index + offset) mod 3: 0 = Buy Day, 1 = Sell Day,
  2 = Sell-Short Day.
* Prior NY-day high/low bound each bar (aggregated by NY day, shifted so
  only completed days are used -- no lookahead).
* Buy-Day long candidate: the bar's low dips to within 0.1xATR of the
  prior day's low and the bar recovers (close > open).
* Sell-Short-Day short candidate: the bar's high rallies to within
  0.1xATR of the prior day's high and rejects (close < open).
* Re-phase: if a Buy Day produces no long candidate, the cycle offset is
  shifted by -1 day for all following days (walked chronologically, so the
  offset on any day depends only on days before it -- no lookahead).

Summary of the rhythm: https://www.smbtraining.com/blog/the-taylor-rhythm
"""

import numpy as np
import pandas as pd

from strategies import base as B

NY_OFFSET_MS = 4 * 3600 * 1000  # NY = UTC - 4h (EDT), fixed across the window
DAY_MS = 86_400_000
# Monday 2026-01-05 00:00 NY == 04:00 UTC: the cycle anchor.
ANCHOR_UTC_MS = 1767585600000

BUY_DAY = 0
SELL_DAY = 1
SELL_SHORT_DAY = 2


def _ny_day(t_ms: pd.Series) -> pd.Series:
    """NY-calendar day index for each bar open (NY = UTC-4)."""
    return ((t_ms - NY_OFFSET_MS) // DAY_MS).astype("int64")


def _rephased_labels(ny_day: np.ndarray, long_cand: np.ndarray) -> np.ndarray:
    """Walk NY days chronologically, applying the -1-day re-phase.

    Whenever a Buy Day ends with no long candidate having fired, the
    cycle offset is decremented for all subsequent days. Labels for day D
    are computed from an offset determined by days < D only.
    """
    labels = np.zeros(len(ny_day), dtype=np.int64)
    anchor_day = (ANCHOR_UTC_MS - NY_OFFSET_MS) // DAY_MS
    offset = 0
    days = np.unique(ny_day)
    for d in days:
        mask = ny_day == d
        label = (int(d - anchor_day) + offset) % 3
        labels[mask] = label
        if label == BUY_DAY and not long_cand[mask].any():
            offset -= 1  # re-phase: the rhythm was out of sync
    return labels


def add_indicators(df: pd.DataFrame, atr_mult: float = 0.1) -> pd.DataFrame:
    df = df.copy()
    ny_day = _ny_day(df["t"])
    df["ny_day"] = ny_day

    # Prior NY-day high/low: per-day aggregates, shifted so only completed
    # days enter; mapped back onto every bar of the current day.
    day_high = df.groupby(ny_day)["h"].transform("max")
    day_low = df.groupby(ny_day)["l"].transform("min")
    day_index = ny_day.values
    prior_high = np.empty(len(df))
    prior_low = np.empty(len(df))
    prior_high[:] = np.nan
    prior_low[:] = np.nan
    for d in np.unique(day_index):
        mask = day_index == d
        prev = day_index == (d - 1)
        if prev.any():
            prior_high[mask] = day_high[prev].iloc[0]
            prior_low[mask] = day_low[prev].iloc[0]
    df["prior_day_high"] = prior_high
    df["prior_day_low"] = prior_low

    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    prox = atr_mult * df["atr"]
    df["long_cand"] = (
        (df["l"] <= df["prior_day_low"] + prox) & (df["c"] > df["o"])
    ).fillna(False)
    df["short_cand"] = (
        (df["h"] >= df["prior_day_high"] - prox) & (df["c"] < df["o"])
    ).fillna(False)
    df["cycle_label"] = _rephased_labels(
        ny_day.to_numpy(), df["long_cand"].to_numpy()
    )
    return df
