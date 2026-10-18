"""Tom DeMark TD Combo indicators (DeMark, "The New Science of Technical
Analysis").

Buy setup: 9 consecutive bars with close < close[4] (flip condition).
Buy countdown: after a completed setup, count 13 bars where each bar has
  close <= low[2], low < prior countdown bar's low, close < prior
  countdown bar's close.  The first countdown bar only needs the
  close <= low[2] condition (no prior countdown bar yet).  Countdown
  bars need not be consecutive (DeMark's Combo rule); a fresh setup
  completion restarts the countdown.  The countdown starts on the bar
  *after* the setup completes.  Sell side mirrors (close > close[4],
  close >= high[2], rising highs/closes).

Defensive simplifications kept: the 9-setup / 13-countdown core and the
directional flip conditions; DeMark's finer rules (setup continuation,
bar-1 countdown qualification against setup bar 9's low, countdown
cancellation on a contrary setup) are approximated by the restart rule.

No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SETUP_BARS = 9
COUNTDOWN_BARS = 13
SETUP_SHIFT = 4
COUNTDOWN_SHIFT = 2


def _consec_true(s: pd.Series, k: int) -> pd.Series:
    """True where s was True on each of the last k bars (NaN -> False)."""
    v = s.astype(float).where(s.notna(), np.nan)
    return (v.rolling(k, min_periods=k).sum() == k).fillna(False)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    h = df["h"]
    l = df["l"]
    cv = c.to_numpy()
    hv = h.to_numpy()
    lv = l.to_numpy()
    n = len(df)

    c4 = c.shift(SETUP_SHIFT)
    buy_setup = _consec_true((c < c4).fillna(False), SETUP_BARS)
    sell_setup = _consec_true((c > c4).fillna(False), SETUP_BARS)
    df["buy_setup_complete"] = buy_setup
    df["sell_setup_complete"] = sell_setup

    buy_done = np.zeros(n, dtype=bool)
    sell_done = np.zeros(n, dtype=bool)
    buy_cnt = np.zeros(n, dtype=int)
    sell_cnt = np.zeros(n, dtype=int)

    b_active = False
    b_count = 0
    b_prev_low = np.nan
    b_prev_close = np.nan
    s_active = False
    s_count = 0
    s_prev_high = np.nan
    s_prev_close = np.nan

    for i in range(n):
        b_just_setup = bool(buy_setup.iloc[i])
        s_just_setup = bool(sell_setup.iloc[i])
        # A setup arms the countdown only when it is not already running;
        # the countdown then begins on the *next* bar.  Setups completing
        # mid-countdown do not restart or pause it (the 13 count runs to
        # completion once armed).
        b_armed_now = b_just_setup and not b_active
        if b_armed_now:
            b_active, b_count = True, 0
            b_prev_low, b_prev_close = np.nan, np.nan
        s_armed_now = s_just_setup and not s_active
        if s_armed_now:
            s_active, s_count = True, 0
            s_prev_high, s_prev_close = np.nan, np.nan

        if b_active and i >= COUNTDOWN_SHIFT and not b_armed_now:
            low2 = lv[i - COUNTDOWN_SHIFT]
            if (
                not np.isnan(low2)
                and cv[i] <= low2
                and (np.isnan(b_prev_low) or lv[i] < b_prev_low)
                and (np.isnan(b_prev_close) or cv[i] < b_prev_close)
            ):
                b_count += 1
                b_prev_low, b_prev_close = lv[i], cv[i]
                if b_count >= COUNTDOWN_BARS:
                    buy_done[i] = True
                    b_active, b_count = False, 0
                    b_prev_low, b_prev_close = np.nan, np.nan
        buy_cnt[i] = b_count

        if s_active and i >= COUNTDOWN_SHIFT and not s_armed_now:
            high2 = hv[i - COUNTDOWN_SHIFT]
            if (
                not np.isnan(high2)
                and cv[i] >= high2
                and (np.isnan(s_prev_high) or hv[i] > s_prev_high)
                and (np.isnan(s_prev_close) or cv[i] > s_prev_close)
            ):
                s_count += 1
                s_prev_high, s_prev_close = hv[i], cv[i]
                if s_count >= COUNTDOWN_BARS:
                    sell_done[i] = True
                    s_active, s_count = False, 0
                    s_prev_high, s_prev_close = np.nan, np.nan
        sell_cnt[i] = s_count

    df["buy_countdown_complete"] = buy_done
    df["sell_countdown_complete"] = sell_done
    df["buy_countdown"] = buy_cnt
    df["sell_countdown"] = sell_cnt
    df["atr"] = B.atr(h, l, c, 14)
    return df
