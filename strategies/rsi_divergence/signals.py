"""RSI regular-divergence signals (Wilder lineage).

  Regular bullish: price prints a lower 5-bar fractal swing low while
    RSI prints a higher low there, RSI < 35 at the second low ->
    pending long; LONG when RSI crosses back above 30 within the next
    20 bars (confirmation), else the setup expires.
  Regular bearish: price higher swing high, RSI lower high, RSI > 65
    at the second high -> SHORT when RSI crosses back below 70 within
    20 bars.

  long_exit / short_exit: none (all False) — exits come from the risk
    module (1.5xATR stop, 2.5xATR trail, 72-bar max hold).

New setups are ignored while a pending confirmation is open, and the
backtest harness ignores entries while a position is open, so this is
effectively one position at a time.

Non-implemented extension: hidden divergence (price higher low + RSI
lower low in an uptrend as a continuation signal) is deliberately not
built here; it answers a different question (trend continuation) and
would need its own entry/exit logic.

Pivots are 5-bar fractals confirmed with the causal 5-bar lag: a pivot
centred at bar j is usable from bar j+5. Both pivots of a divergence
must fall inside a 120-bar window.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_K = 5
DIV_WINDOW = 120
BULL_RSI_MAX = 35.0   # RSI must be under this at the second swing low
BEAR_RSI_MIN = 65.0   # RSI must be over this at the second swing high
CONFIRM_BARS = 20     # pending setup expiry
LONG_CONFIRM = 30.0
SHORT_CONFIRM = 70.0


def _fractal_pivots(values: np.ndarray, k: int, kind: str) -> list:
    n = len(values)
    out = []
    for j in range(k, n - k):
        w = values[j - k:j + k + 1]
        if kind == "low" and int(np.argmin(w)) == k:
            out.append(j)
        elif kind == "high" and int(np.argmax(w)) == k:
            out.append(j)
    return out


def _bull_divergence(lows, closes, rsi, j2, window=DIV_WINDOW,
                     rsi_max=BULL_RSI_MAX) -> bool:
    """Regular bullish divergence at the confirmed price swing low j2."""
    if np.isnan(rsi[j2]) or rsi[j2] >= rsi_max:
        return False
    prev = [j for j in lows if j < j2 and j2 - j <= window]
    if not prev:
        return False
    j1 = prev[-1]
    if np.isnan(rsi[j1]):
        return False
    return bool(closes[j2] < closes[j1] and rsi[j2] > rsi[j1])


def _bear_divergence(highs, closes, rsi, j2, window=DIV_WINDOW,
                     rsi_min=BEAR_RSI_MIN) -> bool:
    """Regular bearish divergence at the confirmed price swing high j2."""
    if np.isnan(rsi[j2]) or rsi[j2] <= rsi_min:
        return False
    prev = [j for j in highs if j < j2 and j2 - j <= window]
    if not prev:
        return False
    j1 = prev[-1]
    if np.isnan(rsi[j1]):
        return False
    return bool(closes[j2] > closes[j1] and rsi[j2] < rsi[j1])


def add_signals(df: pd.DataFrame, pivot_k: int = PIVOT_K,
                rsi_bull_max: float = BULL_RSI_MAX,
                rsi_bear_min: float = BEAR_RSI_MIN,
                confirm_bars: int = CONFIRM_BARS) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    rsi = df["rsi"].to_numpy()

    lows = _fractal_pivots(c, pivot_k, "low")
    highs = _fractal_pivots(c, pivot_k, "high")

    # pending setups keyed by expiry bar
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    pending_long_expiry = -1
    pending_short_expiry = -1

    div_long_at = {}
    for j2 in lows:
        if _bull_divergence(lows, c, rsi, j2, rsi_max=rsi_bull_max):
            div_long_at[j2 + pivot_k] = True   # confirmation bar
    div_short_at = {}
    for j2 in highs:
        if _bear_divergence(highs, c, rsi, j2, rsi_min=rsi_bear_min):
            div_short_at[j2 + pivot_k] = True

    rsi_s = df["rsi"]
    cross_up_30 = B.crossed_above(rsi_s, LONG_CONFIRM).fillna(False).to_numpy()
    cross_dn_70 = B.crossed_below(rsi_s, SHORT_CONFIRM).fillna(False).to_numpy()

    for i in range(n):
        if div_long_at.get(i) and pending_long_expiry < i:
            pending_long_expiry = i + confirm_bars
        if div_short_at.get(i) and pending_short_expiry < i:
            pending_short_expiry = i + confirm_bars
        if pending_long_expiry >= i and cross_up_30[i]:
            long_entry[i] = True
            pending_long_expiry = -1
        if pending_short_expiry >= i and cross_dn_70[i]:
            short_entry[i] = True
            pending_short_expiry = -1
        if pending_long_expiry == i:
            pending_long_expiry = -1
        if pending_short_expiry == i:
            pending_short_expiry = -1

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    return df
