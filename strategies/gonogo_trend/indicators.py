"""GoNoGo Trend -- published-checklist reconstruction (Alex Cole, GoNoGo Charts).

IMPORTANT: the exact GoNoGo formula is proprietary and unpublished. What
follows is a reconstruction from the public checklist GoNoGo describes
(EMA alignment, MACD, ADX/+DI/-DI, Donchian position, RSI vs 50) and
from the Optuma GoNoGo documentation. It reproduces the *structure* --
a -5..+5 composite score mapped to Go / neutral / NoGo states plus a
zero-line oscillator -- not the vendor's exact bars. Treat it as a
GoNoGo-flavoured trend-state engine, not the commercial indicator.

Composite score, one point per component (+1 bullish / -1 bearish / 0
neutral), range -5..+5:

    ema_align : +1 if EMA9 > EMA21 > EMA50, -1 if reversed, else 0
    macd_hist : +1 if MACD(12,26,9) histogram > 0, else -1
    adx_trend : +1 if ADX(14) > 20 and +DI > -DI, -1 if ADX > 20 and
                -DI > +DI, else 0 (no trend, no point either way)
    donchian  : +1 if close sits in the upper third of the Donchian(50)
                range, -1 if in the lower third, else 0
    rsi_mid   : +1 if RSI(14) > 50, -1 if < 50, else 0

States (GoNoGo's own language: Go / "go fish" neutral / NoGo):

    score >= +4  strong Go   (state +2)
    score +2/+3  weak Go     (state +1)
    score -1..+1 neutral     (state  0) -- GoNoGo's amber "go fish"
    score -2/-3  weak NoGo   (state -1)
    score <= -4  strong NoGo (state -2)

Oscillator (GoNoGo Oscillator analogue): a zero-line blend of
MACD-histogram z-score and RSI distance from 50,

    osc = clip(z50(macd_hist) + (RSI - 50) / 25, -6, +6)

where z50 is the histogram divided by its rolling-50 standard
deviation. Positive = momentum with the Go side, negative = with
the NoGo side.

Columns:

    gonogo_score, gonogo_state, gonogo_osc, atr
    (plus the component columns ema9/ema21/ema50, macd_hist,
    adx/plus_di/minus_di, donch_high_50/donch_low_50, rsi)

No lookahead: every component uses data through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_FAST = 9
EMA_MID = 21
EMA_SLOW = 50
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ADX_N = 14
ADX_MIN = 20
DONCHIAN_N = 50
RSI_N = 14
OSC_Z_N = 50
OSC_CLAMP = 6.0


def _ema_alignment(ema9, ema21, ema50):
    up = (ema9 > ema21) & (ema21 > ema50)
    dn = (ema9 < ema21) & (ema21 < ema50)
    return np.where(up, 1.0, np.where(dn, -1.0, 0.0))


def _donchian_position(c, hi, lo):
    """+1 upper third of the Donchian range, -1 lower third, else 0."""
    span = (hi - lo).replace(0.0, np.nan)
    pos = (c - lo) / span
    return np.where(pos >= 2.0 / 3.0, 1.0, np.where(pos <= 1.0 / 3.0, -1.0, 0.0))


def gonogo_score(df: pd.DataFrame) -> pd.DataFrame:
    """Component scores, composite score, state, and oscillator."""
    ema9 = B.ema(df["c"], EMA_FAST)
    ema21 = B.ema(df["c"], EMA_MID)
    ema50 = B.ema(df["c"], EMA_SLOW)
    macd = B.macd(df["c"], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    hist = macd["macd_hist"]
    adx = B.adx(df["h"], df["l"], df["c"], ADX_N)
    don = B.donchian(df["h"], df["l"], DONCHIAN_N)
    rsi = B.rsi(df["c"], RSI_N)

    s_ema = _ema_alignment(ema9, ema21, ema50)
    s_macd = np.where(hist > 0, 1.0, np.where(hist < 0, -1.0, 0.0))
    s_adx = np.where(
        (adx["adx"] > ADX_MIN) & (adx["plus_di"] > adx["minus_di"]),
        1.0,
        np.where(
            (adx["adx"] > ADX_MIN) & (adx["minus_di"] > adx["plus_di"]),
            -1.0,
            0.0,
        ),
    )
    s_don = _donchian_position(df["c"], don[f"donchian_high_{DONCHIAN_N}"],
                               don[f"donchian_low_{DONCHIAN_N}"])
    s_rsi = np.where(rsi > 50, 1.0, np.where(rsi < 50, -1.0, 0.0))

    score = pd.Series(s_ema + s_macd + s_adx + s_don + s_rsi, index=df.index)
    # Mask until every leg is formed: np.where turns NaN comparisons into
    # 0.0, which would fake a neutral score during spin-up. EMA(50) /
    # Donchian(50) are the slowest legs (49 bars); MACD/ADX/RSI form
    # earlier, so masking on those two is sufficient.
    formed = ema50.notna() & don[f"donchian_high_{DONCHIAN_N}"].notna()
    score = score.where(formed)
    state = pd.Series(
        np.where(score >= 4, 2.0,
                 np.where(score >= 2, 1.0,
                          np.where(score <= -4, -2.0,
                                   np.where(score <= -2, -1.0, 0.0)))),
        index=df.index,
    ).where(formed)
    hist_std = hist.rolling(OSC_Z_N, min_periods=OSC_Z_N).std()
    z = hist / hist_std.replace(0.0, np.nan)
    osc = (z + (rsi - 50.0) / 25.0).clip(-OSC_CLAMP, OSC_CLAMP)

    return pd.DataFrame({
        "ema9": ema9, "ema21": ema21, "ema50": ema50,
        "macd_hist": hist,
        "adx": adx["adx"], "plus_di": adx["plus_di"],
        "minus_di": adx["minus_di"],
        f"donchian_high_{DONCHIAN_N}": don[f"donchian_high_{DONCHIAN_N}"],
        f"donchian_low_{DONCHIAN_N}": don[f"donchian_low_{DONCHIAN_N}"],
        "rsi": rsi,
        "gonogo_score": score,
        "gonogo_state": state,
        "gonogo_osc": osc,
    })


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    g = gonogo_score(df)
    for col in g.columns:
        df[col] = g[col]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
