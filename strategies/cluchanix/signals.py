"""ClucHAnix signals — faithful port of populate_buy_trend /
populate_sell_trend from ssssi/freqtrade_strs ClucHAnix.py,
adapted from 1m to 1h bars with the published hyperopt constants.

LONG ENTRY (source, verbatim structure):
    rocr_1h > 0.54904 AND (
        PRIMARY: lower.shift(1) > 0
            AND bbdelta > ha_close * 0.01965
            AND closedelta > ha_close * 0.00556
            AND tail < bbdelta * 0.95089
            AND ha_close < lower.shift(1)
            AND ha_close <= ha_close.shift(1)
        OR ALTERNATIVE: ha_close < ema_slow
            AND ha_close < 0.00799 * lower
    )
Note the alternative path is effectively dormant at the published
constant (0.00799 * lower is ~0.8% of the band — no positive price
is ever below it); it is implemented as written, not repaired.

LONG EXIT (source sell trend, verbatim):
    fisher > 0.38414
    AND ha_high <= ha_high.shift(1)
    AND ha_high.shift(1) <= ha_high.shift(2)
    AND ha_close <= ha_close.shift(1)
    AND ema_fast > ha_close
    AND ha_close * 1.07634 > mid
    AND volume > 0

SHORT side is a builder-added mirror (the source is long-only):
entry mirrors the primary path across the UPPER band
(ha_close > upper.shift(1), ha_close >= ha_close.shift(1),
tail_up < bbdelta * 0.95089) with the ROCR gate reciprocated
(rocr_1h < 1 / 0.54904 — the symmetric dormant gate around the
ratio 1.0) and the alternative path mirrored across the upper
band; exit mirrors the sell trend (fisher < -0.38414, two rising
ha_lows, ha_close >= prior, ema_fast < ha_close,
ha_close * 1.07634 < mid, volume > 0).

A one-position state machine gates entries to flat bars and exits
to the matching side; the harness executes at the next bar's open.
All conditions read bars <= i; no lookahead.
"""

import numpy as np
import pandas as pd

from strategies.cluchanix.indicators import (
    BBDELTA_CLOSE,
    BBDELTA_TAIL,
    CLOSE_BBLOWER,
    CLOSEDDELTA_CLOSE,
    ROCR_1H_MIN,
    SELL_BBMIDDLE_CLOSE,
    SELL_FISHER,
)


def _raw_conditions(df: pd.DataFrame):
    ha_close = df["ha_close"]
    ha_high = df["ha_high"]
    ha_low = df["ha_low"]
    lower = df["lower"]
    upper = df["upper"]
    mid = df["mid"]
    bbdelta = df["bbdelta"]
    closedelta = df["closedelta"]
    tail = df["tail"]
    tail_up = df["tail_up"]
    ema_fast = df["ema_fast"]
    ema_slow = df["ema_slow"]
    fisher = df["fisher"]
    rocr_1h = df["rocr_1h"]
    vol = df["v"]

    rocr_gate_long = rocr_1h > ROCR_1H_MIN
    rocr_gate_short = rocr_1h < (1.0 / ROCR_1H_MIN)

    primary_long = (
        (lower.shift(1) > 0)
        & (bbdelta > ha_close * BBDELTA_CLOSE)
        & (closedelta > ha_close * CLOSEDDELTA_CLOSE)
        & (tail < bbdelta * BBDELTA_TAIL)
        & (ha_close < lower.shift(1))
        & (ha_close <= ha_close.shift(1))
    )
    alt_long = (ha_close < ema_slow) & (
        ha_close < CLOSE_BBLOWER * lower
    )
    long_entry = (rocr_gate_long & (primary_long | alt_long)).fillna(False)

    primary_short = (
        (upper.shift(1) > 0)
        & (bbdelta > ha_close * BBDELTA_CLOSE)
        & (closedelta > ha_close * CLOSEDDELTA_CLOSE)
        & (tail_up < bbdelta * BBDELTA_TAIL)
        & (ha_close > upper.shift(1))
        & (ha_close >= ha_close.shift(1))
    )
    alt_short = (ha_close > ema_slow) & (
        ha_close > upper / CLOSE_BBLOWER
    )
    short_entry = (rocr_gate_short & (primary_short | alt_short)).fillna(False)

    long_exit = (
        (fisher > SELL_FISHER)
        & (ha_high <= ha_high.shift(1))
        & (ha_high.shift(1) <= ha_high.shift(2))
        & (ha_close <= ha_close.shift(1))
        & (ema_fast > ha_close)
        & ((ha_close * SELL_BBMIDDLE_CLOSE) > mid)
        & (vol > 0)
    ).fillna(False)

    short_exit = (
        (fisher < -SELL_FISHER)
        & (ha_low >= ha_low.shift(1))
        & (ha_low.shift(1) >= ha_low.shift(2))
        & (ha_close >= ha_close.shift(1))
        & (ema_fast < ha_close)
        & ((ha_close * SELL_BBMIDDLE_CLOSE) < mid)
        & (vol > 0)
    ).fillna(False)

    return long_entry, short_entry, long_exit, short_exit


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    le_raw, se_raw, lx_raw, sx_raw = _raw_conditions(df)
    le_raw = le_raw.to_numpy(dtype=bool)
    se_raw = se_raw.to_numpy(dtype=bool)
    lx_raw = lx_raw.to_numpy(dtype=bool)
    sx_raw = sx_raw.to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    for i in range(n):
        if pos == "long" and lx_raw[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and sx_raw[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if le_raw[i]:
                le[i] = True
                pos = "long"
            elif se_raw[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
