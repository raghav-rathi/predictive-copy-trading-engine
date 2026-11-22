"""ICT inducement -> sweep -> MSS -> OTE entry (causal, no lookahead).

Pipeline: a single causal state machine scans the bars in order,
using only data through bar i. The full sequence, mechanical
translation of the ICT source (see CALIBRATION.md for every
translation choice):

Bullish (bearish is the exact mirror, all signs flipped):

(a) ORDER BLOCK / POI: a displacement bar — range > 1.5xATR(14)
    closing strongly in the impulse direction (close in the top
    quarter of the range) — marks the POI as the LAST opposing
    (down) candle in the 10 bars before it; the OB zone is that
    candle's [low, high].
(b) INDUCEMENT: the first minor swing low after the displacement
    (3-bar confirmed: low is the minimum over [j-3, j+3], so it
    confirms at bar j+3) whose low sits above the OB top — between
    price and the POI. (Equal lows qualify: the min-window test
    accepts a low equal to a neighbouring low.)
(c) SWEEP: a bar closing below the inducement extreme AND at or
    below the OB top (close into the OB zone).
(d) MSS + DISPLACEMENT + FVG: after the sweep, a close above the
    highest high from the inducement bar through the sweep bar
    (the minor structure high = market-structure shift). The
    confirming bar is the displacement bar itself: in ICT the
    displacement IS what breaks structure, so the break bar must
    also be a displacement bar (range > 1.5xATR(14), strong close)
    leaving a fair-value gap (its low above the high two bars
    earlier). If the break bar is not itself a displacement bar, a
    displacement bar within the next 10 bars still confirms. The
    displacement leg runs from the sweep bar through the
    displacement bar.
(e) OTE ENTRY: the 70.5% retracement level of the displacement
    leg (leg_high - 0.705 * (leg_high - leg_low)). Entry fires on
    the first bar whose low touches the level (limit-style); if no
    retracement within 24 bars the setup is dropped. If price
    closes below the OB low before entry, the POI has failed and
    the setup is dropped.

Timeouts: no inducement within 48 bars of the displacement, no
sweep within 48 bars of the inducement, no MSS within 24 bars of
the sweep, no displacement within 10 bars of the MSS -> the setup
is dropped and the machine returns to idle.

Columns:

    ict_dir       -- +1 on a bullish OTE-entry bar, -1 bearish, else 0
    ict_ote_level -- the 70.5% OTE level on an entry bar, NaN otherwise
    ict_ob_lo     -- OB-zone low on an entry bar, NaN otherwise
    ict_ob_hi     -- OB-zone high on an entry bar, NaN otherwise
    atr           -- Wilder ATR(14)

No lookahead: displacement, swing confirmation, sweep, MSS, FVG
and the OTE touch all read bars <= i; the swing pivot at j is only
used once its [j-3, j+3] window is fully known (bar j+3). A setup
fires exactly once, on its OTE-touch bar.

Related strategies: liquidity_sweep, sfp, order_block_retest and
fvg_mitigation already exist — this one is distinct ONLY as the
FULL sequence (inducement + sweep + MSS + OTE). The source itself
warns inducement is hindsight-friendly; the strict sequence is the
defence, and it fires rarely by design.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_WIN = 14
DISP_MULT = 1.5       # displacement bar: range > 1.5x ATR
STRONG_FRAC = 0.75    # "closing strongly": close in the outer quarter
OB_LOOKBACK = 10      # bars searched back for the last opposing candle
SWING_CONFIRM = 3     # bars each side to confirm a minor swing pivot
INDUCEMENT_TIMEOUT = 48
SWEEP_TIMEOUT = 48
MSS_TIMEOUT = 24
DISP_TIMEOUT = 10
OTE_RET = 0.705       # optimal trade entry retracement of the leg
OTE_DEADLINE = 24     # bars after the displacement leg to retrace


def _is_displacement(rng, atr_v, c, l, direction):
    """range > 1.5xATR and close in the outer quarter in `direction`."""
    if not np.isfinite(atr_v) or rng <= DISP_MULT * atr_v:
        return False
    if direction == 1:
        return c >= l + STRONG_FRAC * rng
    return c <= l + (1 - STRONG_FRAC) * rng


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    atr_v = B.atr(df["h"], df["l"], df["c"], ATR_WIN).to_numpy(dtype=float)

    ict_dir = np.zeros(n, dtype=int)
    ote_level = np.full(n, np.nan)
    ob_lo_col = np.full(n, np.nan)
    ob_hi_col = np.full(n, np.nan)

    state = None  # dict: dir, ob_lo, ob_hi, stage, stage_bar, ...
    for i in range(n):
        rng = h[i] - l[i]
        if state is None:
            if _is_displacement(rng, atr_v[i], c[i], l[i], 1):
                # Last down candle in the lookback -> bullish OB.
                for j in range(i - 1, max(-1, i - 1 - OB_LOOKBACK), -1):
                    if c[j] < o[j]:
                        state = {"dir": 1, "ob_lo": l[j], "ob_hi": h[j],
                                 "stage": "await_inducement",
                                 "stage_bar": i, "disp_bar": i}
                        break
            elif _is_displacement(rng, atr_v[i], c[i], l[i], -1):
                for j in range(i - 1, max(-1, i - 1 - OB_LOOKBACK), -1):
                    if c[j] > o[j]:
                        state = {"dir": -1, "ob_lo": l[j], "ob_hi": h[j],
                                 "stage": "await_inducement",
                                 "stage_bar": i, "disp_bar": i}
                        break
            continue

        d = state["dir"]
        stage = state["stage"]

        if stage == "await_inducement":
            if i - state["stage_bar"] > INDUCEMENT_TIMEOUT:
                state = None
                continue
            j = i - SWING_CONFIRM
            if j > state["disp_bar"] and j >= SWING_CONFIRM:
                if d == 1:
                    # Confirmed swing low: min over [j-3, j+3], fully known.
                    if l[j] == l[j - SWING_CONFIRM:j + SWING_CONFIRM + 1].min() \
                            and l[j] > state["ob_hi"]:
                        state["inducement"] = l[j]
                        state["inducement_bar"] = j
                        state["stage"] = "await_sweep"
                        state["stage_bar"] = i
                else:
                    if h[j] == h[j - SWING_CONFIRM:j + SWING_CONFIRM + 1].max() \
                            and h[j] < state["ob_lo"]:
                        state["inducement"] = h[j]
                        state["inducement_bar"] = j
                        state["stage"] = "await_sweep"
                        state["stage_bar"] = i

        elif stage == "await_sweep":
            if i - state["stage_bar"] > SWEEP_TIMEOUT:
                state = None
                continue
            if d == 1:
                if c[i] < state["inducement"] and c[i] <= state["ob_hi"]:
                    state["sweep_bar"] = i
                    state["mss_level"] = h[state["inducement_bar"]:i + 1].max()
                    state["stage"] = "await_mss"
                    state["stage_bar"] = i
            else:
                if c[i] > state["inducement"] and c[i] >= state["ob_lo"]:
                    state["sweep_bar"] = i
                    state["mss_level"] = l[state["inducement_bar"]:i + 1].min()
                    state["stage"] = "await_mss"
                    state["stage_bar"] = i

        elif stage == "await_mss":
            if i - state["stage_bar"] > MSS_TIMEOUT:
                state = None
                continue
            broke = (d == 1 and c[i] > state["mss_level"]) or (
                d == -1 and c[i] < state["mss_level"]
            )
            if broke:
                # The break bar is usually the displacement bar itself:
                # in ICT the displacement IS what breaks structure. If
                # this bar also qualifies as a displacement bar leaving
                # an FVG, it completes MSS + displacement in one bar.
                if _is_displacement(rng, atr_v[i], c[i], l[i], d):
                    fvg = False
                    if i >= 2:
                        if d == 1:
                            fvg = l[i] > h[i - 2]
                        else:
                            fvg = h[i] < l[i - 2]
                    if fvg:
                        lo = l[state["sweep_bar"]:i + 1].min()
                        hi = h[state["sweep_bar"]:i + 1].max()
                        if d == 1:
                            ote = hi - OTE_RET * (hi - lo)
                        else:
                            ote = lo + OTE_RET * (hi - lo)
                        state["leg_lo"] = lo
                        state["leg_hi"] = hi
                        state["ote"] = ote
                        state["stage"] = "await_ote"
                        state["stage_bar"] = i
                        continue
                state["stage"] = "await_disp"
                state["stage_bar"] = i

        elif stage == "await_disp":
            if i - state["stage_bar"] > DISP_TIMEOUT:
                state = None
                continue
            if _is_displacement(rng, atr_v[i], c[i], l[i], d):
                fvg = False
                if i >= 2:
                    if d == 1:
                        fvg = l[i] > h[i - 2]
                    else:
                        fvg = h[i] < l[i - 2]
                if fvg:
                    lo = l[state["sweep_bar"]:i + 1].min()
                    hi = h[state["sweep_bar"]:i + 1].max()
                    if d == 1:
                        ote = hi - OTE_RET * (hi - lo)
                    else:
                        ote = lo + OTE_RET * (hi - lo)
                    state["leg_lo"] = lo
                    state["leg_hi"] = hi
                    state["ote"] = ote
                    state["stage"] = "await_ote"
                    state["stage_bar"] = i

        elif stage == "await_ote":
            if d == 1:
                if l[i] <= state["ote"]:
                    ict_dir[i] = 1
                    ote_level[i] = state["ote"]
                    ob_lo_col[i] = state["ob_lo"]
                    ob_hi_col[i] = state["ob_hi"]
                    state = None
                    continue
                if c[i] < state["ob_lo"]:
                    state = None  # POI failed before the retracement
                    continue
            else:
                if h[i] >= state["ote"]:
                    ict_dir[i] = -1
                    ote_level[i] = state["ote"]
                    ob_lo_col[i] = state["ob_lo"]
                    ob_hi_col[i] = state["ob_hi"]
                    state = None
                    continue
                if c[i] > state["ob_hi"]:
                    state = None
                    continue
            if i - state["stage_bar"] > OTE_DEADLINE:
                state = None

    df["ict_dir"] = ict_dir
    df["ict_ote_level"] = ote_level
    df["ict_ob_lo"] = ob_lo_col
    df["ict_ob_hi"] = ob_hi_col
    df["atr"] = atr_v
    return df
