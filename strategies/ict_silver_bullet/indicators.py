"""ICT Silver Bullet killzone indicators (Michael Huddleston, 2022 mentorship).

t is ms UTC. The whole backtest window (2026-03-14 -> 2026-10-18) sits
inside US daylight time (2026 DST: Mar 8 -> Nov 1), so NY = UTC-4h is
used for every bar -- documented assumption, no DST transition inside
the window. Killzones (NY): 03:00-04:00, 10:00-11:00, 14:00-15:00; a 1h
bar belongs to the killzone its *open* falls in.

HTF bias: 1h closes resampled to 4h, EMA(50) on the 4h closes, aligned
to each 1h bar via the latest 4h bar fully closed by that bar's close
(merge_asof on close_time - 4h, backward). Bullish bias when the 4h EMA
is rising. No lookahead: the just-forming 4h bar is never consumed.

FVG: bullish gap low[i] > high[i-2] (bearish: high[i] < low[i-2]). Gaps
are tracked per NY day; a gap stays unmitigated until a later same-day
bar's range overlaps it. bull_fvg_touch marks bars overlapping an
unmitigated bullish gap printed earlier the same NY day. Gaps do not
carry across NY days ("earlier this session").

MSS: 3-bar micro swing high = strict pivot high with one bar each side;
mss_bull = close above the last fully-confirmed micro swing high.
Mirror for bears.
"""

import numpy as np
import pandas as pd

from strategies import base as B

KILLZONE_HOURS = (3, 10, 14)
NY_OFFSET_MS = 4 * 3_600_000  # EDT = UTC-4 for the whole window (see docstring)
HTF_RULE = "4h"
HTF_EMA = 50


def _ny_fields(t_ms: np.ndarray):
    ny_hour = ((t_ms // 3_600_000) - 4) % 24
    ny_day = (t_ms - NY_OFFSET_MS) // 86_400_000
    return ny_hour, ny_day


def _htf_bias(df: pd.DataFrame):
    """Return (bias_bull, bias_bear) bool arrays aligned to df's 1h bars."""
    n = len(df)
    t = df["t"].to_numpy()
    dt = pd.to_datetime(t, unit="ms", utc=True)
    s = pd.Series(df["c"].to_numpy(), index=dt).sort_index()
    htf = s.resample(HTF_RULE).last().dropna()
    ema = B.ema(htf, HTF_EMA)
    tbl = pd.DataFrame(
        {
            "t4": htf.index,
            "bull": (ema > ema.shift(1)).fillna(False).to_numpy(),
            "bear": (ema < ema.shift(1)).fillna(False).to_numpy(),
        }
    ).sort_values("t4")
    # latest 4h bar fully closed by this 1h bar's close: left-label L
    # closes at L+4h <= close_time  <=>  L <= open + 1h - 4h
    keys = pd.DataFrame({"tc": dt - pd.to_timedelta(3, unit="h")})
    aligned = pd.merge_asof(keys, tbl, left_on="tc", right_on="t4",
                            direction="backward")
    bull = aligned["bull"].fillna(False).to_numpy(dtype=bool)
    bear = aligned["bear"].fillna(False).to_numpy(dtype=bool)
    assert len(bull) == n
    return bull, bear


def _fvg_touches(df: pd.DataFrame, ny_day: np.ndarray):
    """Per-NY-day FVG tracking -> (bull_touch, bear_touch) bool arrays."""
    n = len(df)
    l = df["l"].to_numpy()
    h = df["h"].to_numpy()
    bull_touch = np.zeros(n, dtype=bool)
    bear_touch = np.zeros(n, dtype=bool)
    for d in np.unique(ny_day):
        idx = np.flatnonzero(ny_day == d)
        bull_gaps: list = []  # (top, bot), None once mitigated
        bear_gaps: list = []
        for i in idx:
            li, hi = l[i], h[i]
            for gi, (top, bot) in enumerate(bull_gaps):
                if top is not None and li <= top and hi >= bot:
                    bull_touch[i] = True
                    bull_gaps[gi] = (None, None)
            for gi, (top, bot) in enumerate(bear_gaps):
                if top is not None and li <= top and hi >= bot:
                    bear_touch[i] = True
                    bear_gaps[gi] = (None, None)
            # gaps printed on this bar are only touchable from the next bar
            if i >= 2 and l[i] > h[i - 2]:
                bull_gaps.append((float(l[i]), float(h[i - 2])))
            if i >= 2 and h[i] < l[i - 2]:
                bear_gaps.append((float(l[i - 2]), float(h[i])))
    return bull_touch, bear_touch


def _mss(df: pd.DataFrame):
    """Market-structure shift vs last confirmed 3-bar micro swing."""
    h, l, c = df["h"], df["l"], df["c"]
    piv_high = (h > h.shift(1)) & (h > h.shift(-1))
    piv_low = (l < l.shift(1)) & (l < l.shift(-1))
    last_ph = h.where(piv_high).ffill().shift(1)
    last_pl = l.where(piv_low).ffill().shift(1)
    mss_bull = (c > last_ph).fillna(False)
    mss_bear = (c < last_pl).fillna(False)
    return mss_bull.to_numpy(dtype=bool), mss_bear.to_numpy(dtype=bool)


def add_indicators(df: pd.DataFrame, killzones: tuple = KILLZONE_HOURS) -> pd.DataFrame:
    df = df.copy()
    t = df["t"].to_numpy()
    ny_hour, ny_day = _ny_fields(t)
    df["ny_hour"] = ny_hour
    df["ny_day"] = ny_day
    df["in_killzone"] = pd.Series(ny_hour, index=df.index).isin(killzones)
    bias_bull, bias_bear = _htf_bias(df)
    df["bias_bull"] = pd.Series(bias_bull, index=df.index)
    df["bias_bear"] = pd.Series(bias_bear, index=df.index)
    bull_touch, bear_touch = _fvg_touches(df, ny_day)
    df["bull_fvg_touch"] = pd.Series(bull_touch, index=df.index)
    df["bear_fvg_touch"] = pd.Series(bear_touch, index=df.index)
    mss_bull, mss_bear = _mss(df)
    df["mss_bull"] = pd.Series(mss_bull, index=df.index)
    df["mss_bear"] = pd.Series(mss_bear, index=df.index)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
