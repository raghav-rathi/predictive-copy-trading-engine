"""Fibonacci time zones as a timing filter on pullback entries.

Fibonacci time zones are vertical lines drawn at Fibonacci bar
counts after a swing anchor: here 8, 13, 21 and 34 bars after the
most recent confirmed swing high/low. Time zones alone give
timing, not direction — they mark the bars where a turn is
*likely*, not which way price will go. The direction in this
strategy comes from an EMA pullback confirmation inside the zone
window (see below).

Anchor: the most recent confirmed 10-bar swing high/low. A swing
high at centre j iff h[j] is the max of the 10 bars h[j-7..j+2]
(strictly above its left neighbour); a swing low iff l[j] is the
min of l[j-7..j+2]. A pivot is recorded at its confirmation bar
(centre+2). A newly confirmed swing re-anchors the zones.

Zone window: a bar counts as "in the zone" if it is within +/-1
bar of a zone count (anchor bar + 8 / 13 / 21 / 34).

Bullish setup (anchor was a swing LOW): the trend filter is
close > EMA(50) (uptrend). A pullback is a close below EMA(20)
at any point since the anchor bar, followed by a close back above
EMA(20) — the reclaim bar must fall inside a zone window (and
must be a genuine cross back above: the previous bar's close was
at or below its EMA(20)). That reclaim bar is the long_trigger.
Bearish is the mirror (anchor was a swing HIGH, close < EMA(50),
rally above EMA(20) then a close back below it inside a zone
window). If no confirmation lands inside the +/-1-bar window,
the zone passes with no trade.

Columns:
    ema20 / ema50 -- exponential moving averages of close
    anchor_bar -- centre bar of the anchoring swing (NaN: none yet)
    anchor_kind -- +1 anchor is a swing low, -1 a swing high, 0 none
    anchor_price -- price of the anchoring swing
    anchor_low / anchor_high -- most recent confirmed swing low /
        swing high price, forward-filled (exit levels)
    in_zone -- True on a bar inside a zone window
    fib_state -- 0 no anchor, 1 anchor active, 2 in zone,
        3 in zone and pullback/rally armed (max over the two sides)
    long_trigger / short_trigger -- True only on the entry bar

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_BACK = 7   # pivot window is bars [j-7, j+2] (10 bars)
PIVOT_FWD = 2    # confirmation at centre+2
ZONE_COUNTS = (8, 13, 21, 34)
ZONE_TOL = 1

INDICATOR_COLS = [
    "ema20",
    "ema50",
    "anchor_bar",
    "anchor_kind",
    "anchor_price",
    "anchor_low",
    "anchor_high",
    "in_zone",
    "fib_state",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["ema20"] = B.ema(df["c"], 20)
    df["ema50"] = B.ema(df["c"], 50)
    ema20 = df["ema20"].to_numpy(dtype=float)
    ema50 = df["ema50"].to_numpy(dtype=float)

    anchor_bar = np.full(n, np.nan)
    anchor_kind = np.zeros(n, dtype=int)
    anchor_price = np.full(n, np.nan)
    anchor_low = np.full(n, np.nan)
    anchor_high = np.full(n, np.nan)
    in_zone = np.zeros(n, dtype=bool)
    fib_state = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    cur_anchor_bar = None   # centre bar of the anchoring swing
    cur_anchor_price = np.nan
    cur_anchor_kind = 0     # +1 low, -1 high
    last_low = np.nan
    last_high = np.nan
    below20 = False  # a close below EMA(20) has printed since the anchor
    above20 = False  # a close above EMA(20) has printed since the anchor

    for i in range(n):
        # ---- pivot confirmation for centre j = i-2 ----
        new_low = None
        new_high = None
        j = i - PIVOT_FWD
        if j >= PIVOT_BACK:
            if (h[j] == h[j - PIVOT_BACK:j + PIVOT_FWD + 1].max()
                    and h[j] > h[j - 1]):
                new_high = (float(h[j]), j)
            if (l[j] == l[j - PIVOT_BACK:j + PIVOT_FWD + 1].min()
                    and l[j] < l[j - 1]):
                new_low = (float(l[j]), j)
        # A newly confirmed swing re-anchors the zones. (If one bar
        # somehow confirms both a high and a low, the high wins;
        # that needs a single bar to be both extremes of its window.)
        if new_low is not None:
            last_low = new_low[0]
            cur_anchor_bar, cur_anchor_price, cur_anchor_kind = (
                new_low[1], new_low[0], 1)
            below20 = any(
                np.isfinite(ema20[k]) and c[k] < ema20[k]
                for k in range(new_low[1], i + 1))
            above20 = False
        if new_high is not None:
            last_high = new_high[0]
            cur_anchor_bar, cur_anchor_price, cur_anchor_kind = (
                new_high[1], new_high[0], -1)
            above20 = any(
                np.isfinite(ema20[k]) and c[k] > ema20[k]
                for k in range(new_high[1], i + 1))
            below20 = False

        # ---- zone window? ----
        zone = False
        if cur_anchor_bar is not None:
            for zc in ZONE_COUNTS:
                if abs(i - (cur_anchor_bar + zc)) <= ZONE_TOL:
                    zone = True
                    break

        # ---- pullback / rally tracking since the anchor ----
        if cur_anchor_kind == 1 and np.isfinite(ema20[i]) and c[i] < ema20[i]:
            below20 = True
        if cur_anchor_kind == -1 and np.isfinite(ema20[i]) and c[i] > ema20[i]:
            above20 = True

        # ---- entries: EMA pullback confirmation inside the zone ----
        if (zone and cur_anchor_kind == 1 and below20
                and np.isfinite(ema20[i]) and np.isfinite(ema50[i])
                and c[i] > ema50[i] and c[i] > ema20[i]
                and i > 0 and np.isfinite(ema20[i - 1])
                and c[i - 1] <= ema20[i - 1]):
            long_trig[i] = True
            below20 = False
        if (zone and cur_anchor_kind == -1 and above20
                and np.isfinite(ema20[i]) and np.isfinite(ema50[i])
                and c[i] < ema50[i] and c[i] < ema20[i]
                and i > 0 and np.isfinite(ema20[i - 1])
                and c[i - 1] >= ema20[i - 1]):
            short_trig[i] = True
            above20 = False

        # ---- record this bar ----
        anchor_bar[i] = float(cur_anchor_bar) if cur_anchor_bar is not None else np.nan
        anchor_kind[i] = cur_anchor_kind
        anchor_price[i] = cur_anchor_price
        anchor_low[i] = last_low
        anchor_high[i] = last_high
        in_zone[i] = zone
        if zone and ((cur_anchor_kind == 1 and below20)
                     or (cur_anchor_kind == -1 and above20)):
            fib_state[i] = 3
        elif zone:
            fib_state[i] = 2
        elif cur_anchor_bar is not None:
            fib_state[i] = 1
        else:
            fib_state[i] = 0

    df["anchor_bar"] = anchor_bar
    df["anchor_kind"] = anchor_kind
    df["anchor_price"] = anchor_price
    df["anchor_low"] = anchor_low
    df["anchor_high"] = anchor_high
    df["in_zone"] = in_zone
    df["fib_state"] = fib_state
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
