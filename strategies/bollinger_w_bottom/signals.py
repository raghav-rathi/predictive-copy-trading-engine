"""Bollinger W-bottom / M-top signals (John Bollinger).

W-bottom (long), per bar i using only data through bar i's close:

  (a) First low: a bar with %B < 0. The most extreme such bar (lowest
      %B) while waiting counts as the first low.
  (b) Rally: a later bar closes above the middle band.
  (c) Second low: within 40 bars of the rally, a bar whose close is
      lower than or within 1% of the first low's close AND whose %B
      is higher than the first low's %B (bullish %B divergence).
  (d) Long entry: the first close above the middle band after the
      second low.

M-top (short) is the exact mirror: first high %B > 1, dip below the
middle band, second high within 40 bars of the dip whose close is
higher than or within 1% of the first high's close with a LOWER %B,
entry on the first close below the middle band.

Staleness guards (mechanical choices, see CALIBRATION.md): a first
low older than 40 bars when the rally arrives is dropped, and a
second low / confirmation more than 40 bars after the rally / second
low is dropped. A new %B extreme during the wait restarts the pattern
from that bar as the first low / high.

Exits: long on close below the middle band; short on close above it.

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The harness executes at bar i+1's open.
"""

import numpy as np
import pandas as pd

PATTERN_WINDOW = 40      # bars allowed between pattern stages
PRICE_TOL = 0.01         # second low/high within 1% of the first

# Long-side states.
_IDLE, _RALLY_WAIT, _SECOND_LOW_WAIT, _CONFIRM_WAIT = range(4)
# Short-side states (mirror).
_S_IDLE, _DIP_WAIT, _SECOND_HIGH_WAIT, _S_CONFIRM_WAIT = range(4)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    pctb = df["pctb"].to_numpy(dtype=float)
    mid = df["bb_mid"].to_numpy(dtype=float)
    close = df["c"].to_numpy(dtype=float)

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    # Long-side pattern state.
    state = _IDLE
    first_low_idx = -1
    first_low_price = np.nan
    first_low_pctb = np.nan
    rally_idx = -1
    second_low_idx = -1

    # Short-side pattern state.
    s_state = _S_IDLE
    first_high_idx = -1
    first_high_price = np.nan
    first_high_pctb = np.nan
    dip_idx = -1
    second_high_idx = -1

    for i in range(n):
        p = pctb[i]
        m = mid[i]
        c = close[i]

        # --- W-bottom (long) state machine ---
        if state == _IDLE:
            if p < 0:
                state = _RALLY_WAIT
                first_low_idx, first_low_price, first_low_pctb = i, c, p
        elif state == _RALLY_WAIT:
            if p < first_low_pctb:
                # More extreme low supersedes the first low.
                first_low_idx, first_low_price, first_low_pctb = i, c, p
            elif c > m:
                state = _SECOND_LOW_WAIT
                rally_idx = i
            elif i - first_low_idx > PATTERN_WINDOW:
                state = _IDLE
        elif state == _SECOND_LOW_WAIT:
            if p < first_low_pctb:
                # New extreme low restarts the pattern.
                state = _RALLY_WAIT
                first_low_idx, first_low_price, first_low_pctb = i, c, p
            elif c <= (1.0 + PRICE_TOL) * first_low_price and p > first_low_pctb:
                state = _CONFIRM_WAIT
                second_low_idx = i
            elif i - rally_idx > PATTERN_WINDOW:
                state = _IDLE
        elif state == _CONFIRM_WAIT:
            if p < first_low_pctb:
                state = _RALLY_WAIT
                first_low_idx, first_low_price, first_low_pctb = i, c, p
            elif c > m:
                long_entry[i] = True
                state = _IDLE
            elif i - second_low_idx > PATTERN_WINDOW:
                state = _IDLE

        # --- M-top (short) state machine (mirror) ---
        if s_state == _S_IDLE:
            if p > 1:
                s_state = _DIP_WAIT
                first_high_idx, first_high_price, first_high_pctb = i, c, p
        elif s_state == _DIP_WAIT:
            if p > first_high_pctb:
                first_high_idx, first_high_price, first_high_pctb = i, c, p
            elif c < m:
                s_state = _SECOND_HIGH_WAIT
                dip_idx = i
            elif i - first_high_idx > PATTERN_WINDOW:
                s_state = _S_IDLE
        elif s_state == _SECOND_HIGH_WAIT:
            if p > first_high_pctb:
                s_state = _DIP_WAIT
                first_high_idx, first_high_price, first_high_pctb = i, c, p
            elif c >= (1.0 - PRICE_TOL) * first_high_price and p < first_high_pctb:
                s_state = _S_CONFIRM_WAIT
                second_high_idx = i
            elif i - dip_idx > PATTERN_WINDOW:
                s_state = _S_IDLE
        elif s_state == _S_CONFIRM_WAIT:
            if p > first_high_pctb:
                s_state = _DIP_WAIT
                first_high_idx, first_high_price, first_high_pctb = i, c, p
            elif c < m:
                short_entry[i] = True
                s_state = _S_IDLE
            elif i - second_high_idx > PATTERN_WINDOW:
                s_state = _S_IDLE

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = (df["c"] < df["bb_mid"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > df["bb_mid"]).fillna(False).astype(bool)
    return df
