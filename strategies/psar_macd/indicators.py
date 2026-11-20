"""Parabolic SAR + MACD agreement indicators.

Parabolic SAR (Wilder, step 0.02, max AF 0.20) implemented from
scratch here — seeded LONG from bar 0 only (SAR = low[0],
EP = high[0], AF = 0.02); the first two closes are never used to
seed bar 0. On each later bar the SAR is advanced by AF * (EP - SAR),
clamped so it never exceeds the prior two lows (long) or highs
(short); a close through the SAR flips the trend, the SAR is reset
to the prior extreme point, and EP/AF restart. MACD(12, 26, 9)
line vs signal supplies the agreement filter.

Columns:
    psar / psar_dir -- SAR value and direction (+1 SAR below price
        / -1 SAR above price; defined from bar 0, never NaN)
    macd / macd_signal / macd_hist -- MACD line, signal, histogram
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PSAR_STEP = 0.02
PSAR_MAX_AF = 0.20
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["psar", "psar_dir", "macd", "macd_signal",
                  "macd_hist", "atr"]


def psar(h, l, c, step: float = PSAR_STEP,
         max_af: float = PSAR_MAX_AF) -> pd.DataFrame:
    """Wilder Parabolic SAR. Returns SAR value and direction."""
    h_v = np.asarray(h, dtype=float)
    l_v = np.asarray(l, dtype=float)
    c_v = np.asarray(c, dtype=float)
    n = len(c_v)
    sar = np.full(n, np.nan)
    direction = np.full(n, np.nan)
    if n == 0:
        return pd.DataFrame({"psar": sar, "psar_dir": direction},
                            index=c.index)
    # Seed LONG from bar 0 only.
    trend = 1
    s = float(l_v[0])
    ep = float(h_v[0])
    af = float(step)
    sar[0] = s
    direction[0] = 1.0
    for i in range(1, n):
        s = s + af * (ep - s)
        if trend == 1:
            s = min(s, l_v[i - 1])
            if i >= 2:
                s = min(s, l_v[i - 2])
            if c_v[i] < s:
                # Flip to short: SAR resets to the prior extreme.
                trend = -1
                s = ep
                ep = float(l_v[i])
                af = float(step)
            else:
                if h_v[i] > ep:
                    ep = float(h_v[i])
                    af = min(af + step, max_af)
        else:
            s = max(s, h_v[i - 1])
            if i >= 2:
                s = max(s, h_v[i - 2])
            if c_v[i] > s:
                # Flip to long: SAR resets to the prior extreme.
                trend = 1
                s = ep
                ep = float(h_v[i])
                af = float(step)
            else:
                if l_v[i] < ep:
                    ep = float(l_v[i])
                    af = min(af + step, max_af)
        sar[i] = s
        direction[i] = float(trend)
    return pd.DataFrame({"psar": sar, "psar_dir": direction}, index=c.index)


def add_indicators(df: pd.DataFrame, step: float = PSAR_STEP,
                   max_af: float = PSAR_MAX_AF,
                   macd_fast: int = MACD_FAST, macd_slow: int = MACD_SLOW,
                   macd_signal: int = MACD_SIGNAL) -> pd.DataFrame:
    df = df.copy()
    p = psar(df["h"], df["l"], df["c"], step, max_af)
    df["psar"] = p["psar"]
    df["psar_dir"] = p["psar_dir"]
    m = B.macd(df["c"], macd_fast, macd_slow, macd_signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
