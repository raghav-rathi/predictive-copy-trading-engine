"""Victor Sperandeo 1-2-3 trend-change signals (Trader Vic).

Bearish 1-2-3 (bullish mirrors it):
  (1) the close breaks below the up-trend line. The line connects the
      lowest 5-bar pivot low to the highest later 5-bar pivot low (over
      a 200-bar lookback) such that the line never crosses price
      between them (every in-between low stays >= the line).
  (2) retest: the first 5-bar pivot high after the break that fails to
      exceed the break-bar high becomes point 2; if a pivot high takes
      out the break-bar high the pattern is invalidated.
  (3) a close below the interim swing low (lowest low between point 1
      and point 2) -> short_entry.
A stale pattern (no completion within PATTERN_TIMEOUT bars) is dropped.
Exits: the opposite 1-2-3 completion reverses the position; the hard
stop / 2R target / max hold come from risk.py.

No lookahead: at bar i only pivots formed at bars <= i-2 are consumed.
"""

import numpy as np
import pandas as pd

LOOKBACK = 200
PATTERN_TIMEOUT = 72


def _fit_uptrend(low: np.ndarray, piv_idx: np.ndarray, i: int, lookback: int):
    """(anchor_bar, anchor_px, slope) of the valid up-trend line at bar i.

    Lowest pivot low in [i-lookback, i-2], then the highest later pivot
    low whose connecting line never dips below any in-between low.
    None when fewer than two pivots or no valid second anchor.
    """
    js = piv_idx[(piv_idx >= i - lookback) & (piv_idx <= i - 2)]
    if len(js) < 2:
        return None
    ja = js[int(np.argmin(low[js]))]
    px_a = float(low[ja])
    cand = js[js > ja]
    if len(cand) == 0:
        return None
    order = cand[np.argsort(-low[cand], kind="stable")]
    for jb in order:
        jb = int(jb)
        slope = (float(low[jb]) - px_a) / (jb - ja)
        ks = np.arange(ja + 1, jb)
        if ks.size and bool(np.any(low[ks] < px_a + slope * (ks - ja) - 1e-9)):
            continue
        return ja, px_a, slope
    return None


def _fit_downtrend(high: np.ndarray, piv_idx: np.ndarray, i: int, lookback: int):
    """Mirror of _fit_uptrend: highest pivot high, then the lowest later
    pivot high whose line never rises above any in-between high."""
    js = piv_idx[(piv_idx >= i - lookback) & (piv_idx <= i - 2)]
    if len(js) < 2:
        return None
    ja = js[int(np.argmax(high[js]))]
    px_a = float(high[ja])
    cand = js[js > ja]
    if len(cand) == 0:
        return None
    order = cand[np.argsort(high[cand], kind="stable")]
    for jb in order:
        jb = int(jb)
        slope = (float(high[jb]) - px_a) / (jb - ja)
        ks = np.arange(ja + 1, jb)
        if ks.size and bool(np.any(high[ks] > px_a + slope * (ks - ja) + 1e-9)):
            continue
        return ja, px_a, slope
    return None


def add_signals(df: pd.DataFrame, lookback: int = LOOKBACK) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    low = df["l"].to_numpy()
    high = df["h"].to_numpy()
    close = df["c"].to_numpy()
    pivL = np.flatnonzero(df["piv_low"].fillna(False).to_numpy())
    pivH = np.flatnonzero(df["piv_high"].fillna(False).to_numpy())

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    # bearish pattern state: 0 flat, 1 broken awaiting retest, 2 armed
    b_state, b_p1, b_break_high, b_p2, b_entry_low = 0, -1, np.nan, -1, np.nan
    # bullish pattern state
    s_state, s_p1, s_break_low, s_p2, s_entry_high = 0, -1, np.nan, -1, np.nan

    for i in range(n):
        # ---------------- bearish 1-2-3 ----------------
        if b_state == 0:
            up = _fit_uptrend(low, pivL, i, lookback)
            if up is not None and i > 0:
                ja, px_a, slope = up
                line_i = px_a + slope * (i - ja)
                line_im1 = px_a + slope * (i - 1 - ja)
                if close[i - 1] >= line_im1 and close[i] < line_i:
                    b_state, b_p1, b_break_high = 1, i, float(high[i])
        elif b_state == 1:
            if i - b_p1 > PATTERN_TIMEOUT:
                b_state = 0
            else:
                cands = pivH[(pivH > b_p1) & (pivH <= i - 2)]
                if len(cands):
                    j = int(cands[0])
                    if float(high[j]) < b_break_high:
                        b_state, b_p2 = 2, j
                        b_entry_low = float(low[b_p1 : j + 1].min())
                    else:
                        b_state = 0  # retest took out the break-bar high
        elif b_state == 2:
            if i - b_p1 > PATTERN_TIMEOUT:
                b_state = 0
            else:
                cands = pivH[(pivH > b_p2) & (pivH <= i - 2)]
                if len(cands) and float(high[cands].max()) >= b_break_high:
                    b_state = 0  # higher high invalidates the reversal
                elif close[i] < b_entry_low:
                    short_entry[i] = True
                    b_state = 0
        # ---------------- bullish 1-2-3 ----------------
        if s_state == 0:
            dn = _fit_downtrend(high, pivH, i, lookback)
            if dn is not None and i > 0:
                ja, px_a, slope = dn
                line_i = px_a + slope * (i - ja)
                line_im1 = px_a + slope * (i - 1 - ja)
                if close[i - 1] <= line_im1 and close[i] > line_i:
                    s_state, s_p1, s_break_low = 1, i, float(low[i])
        elif s_state == 1:
            if i - s_p1 > PATTERN_TIMEOUT:
                s_state = 0
            else:
                cands = pivL[(pivL > s_p1) & (pivL <= i - 2)]
                if len(cands):
                    j = int(cands[0])
                    if float(low[j]) > s_break_low:
                        s_state, s_p2 = 2, j
                        s_entry_high = float(high[s_p1 : j + 1].max())
                    else:
                        s_state = 0  # retest took out the break-bar low
        elif s_state == 2:
            if i - s_p1 > PATTERN_TIMEOUT:
                s_state = 0
            else:
                cands = pivL[(pivL > s_p2) & (pivL <= i - 2)]
                if len(cands) and float(low[cands].min()) <= s_break_low:
                    s_state = 0  # lower low invalidates the reversal
                elif close[i] > s_entry_high:
                    long_entry[i] = True
                    s_state = 0

    df["long_entry"] = pd.Series(long_entry, index=df.index)
    df["short_entry"] = pd.Series(short_entry, index=df.index)
    # the opposite 1-2-3 completion reverses the position
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
