"""Adaptive Supertrend -- Supertrend (Olivier Seban) with a
volatility-regime-adaptive ATR multiplier driven by the Choppiness
Index (E.W. Dreiss).

    ATR(10)           -- Wilder ATR, the volatility gauge
    CHOP(14)          -- 100 * log10( sum(TR,14) / (max(H,14)-min(L,14)) )
                         / log10(14); <38 trending, >62 choppy
    k (per bar)       -- chop < 38 -> 2.0 (tight, trending: ride it)
                         chop > 62 -> 4.0 (wide, choppy: stop flipping)
                         else      -> 3.0 (classic default)
    upper/lower band  -- HL2 +/- k * ATR(10), with k varying per bar
    supertrend line   -- the classic final-band ratchet (see
                         strategies.base.supertrend) run with the
                         per-bar bands: final upper only falls, final
                         lower only rises; direction flips when close
                         crosses the opposite final band.

The adaptive loop is implemented here rather than reusing
strategies.base.supertrend because that helper takes a fixed k;
the loop logic (final-band ratchet + direction flip on close through
the opposite band) is identical, only the band inputs vary per bar.

Columns:
    chop              -- Choppiness Index(14) (NaN until 14 bars)
    k_mult            -- per-bar ATR multiplier (2.0 / 3.0 / 4.0)
    atr               -- Wilder ATR(10)
    supertrend        -- adaptive Supertrend line
    supertrend_dir    -- +1 up / -1 down (NaN before first valid ATR)
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 10
CHOP_N = 14
CHOP_TREND = 38.0   # below this: trending -> tight multiplier
CHOP_CHOPPY = 62.0  # above this: choppy -> wide multiplier
K_TREND = 2.0
K_DEFAULT = 3.0
K_CHOPPY = 4.0


def choppiness(h: pd.Series, l: pd.Series, c: pd.Series,
               n: int = CHOP_N) -> pd.Series:
    """Choppiness Index(14). NaN until n bars; NaN on a zero-range window."""
    tr = B.true_range(h, l, c)
    sum_tr = tr.rolling(n, min_periods=n).sum()
    max_hi = h.rolling(n, min_periods=n).max()
    min_lo = l.rolling(n, min_periods=n).min()
    window_range = max_hi - min_lo
    ratio = sum_tr / window_range.replace(0, np.nan)
    chop = 100 * np.log10(ratio) / np.log10(n)
    return chop.where((ratio > 0) & np.isfinite(ratio))


def multiplier_from_chop(chop: pd.Series) -> pd.Series:
    """Per-bar ATR multiplier from the Choppiness Index.

    NaN chop (warmup / flat window) maps to the classic default k=3.0.
    """
    k = pd.Series(np.full(len(chop), K_DEFAULT), index=chop.index, dtype=float)
    k = k.where(~(chop < CHOP_TREND), K_TREND)
    k = k.where(~(chop > CHOP_CHOPPY), K_CHOPPY)
    return k


def adaptive_supertrend(h: pd.Series, l: pd.Series, c: pd.Series,
                        k: pd.Series, atr_n: int = ATR_N) -> pd.DataFrame:
    """Supertrend with a per-bar multiplier series.

    Same final-band ratchet as strategies.base.supertrend, with the
    upper/lower bands rebuilt each bar from that bar's k. Returns the
    line and direction (+1 up / -1 down).
    """
    a = B.atr(h, l, c, atr_n)
    hl2 = (h + l) / 2
    k_v = k.to_numpy(dtype=float)
    ub_v = (hl2 + k_v * a).to_numpy()
    lb_v = (hl2 - k_v * a).to_numpy()
    c_v = c.to_numpy()
    m = len(c)
    fub = np.full(m, np.nan)
    flb = np.full(m, np.nan)
    d = np.full(m, np.nan)
    valid = np.where(~np.isnan(ub_v) & ~np.isnan(lb_v))[0]
    if len(valid) == 0:
        return pd.DataFrame({"supertrend": fub, "supertrend_dir": d}, index=c.index)
    j = valid[0]
    fub[j] = ub_v[j]
    flb[j] = lb_v[j]
    d[j] = 1.0 if c_v[j] >= (ub_v[j] + lb_v[j]) / 2 else -1.0
    for i in range(j + 1, m):
        fub[i] = ub_v[i] if (ub_v[i] < fub[i - 1] or c_v[i - 1] > fub[i - 1]) else fub[i - 1]
        flb[i] = lb_v[i] if (lb_v[i] > flb[i - 1] or c_v[i - 1] < flb[i - 1]) else flb[i - 1]
        if d[i - 1] == 1:
            d[i] = -1 if c_v[i] < flb[i - 1] else 1
        else:
            d[i] = 1 if c_v[i] > fub[i - 1] else -1
    line = np.where(d == 1, flb, fub)
    return pd.DataFrame({"supertrend": line, "supertrend_dir": d}, index=c.index)


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N,
                   chop_n: int = CHOP_N) -> pd.DataFrame:
    df = df.copy()
    chop = choppiness(df["h"], df["l"], df["c"], chop_n)
    k = multiplier_from_chop(chop)
    st = adaptive_supertrend(df["h"], df["l"], df["c"], k, atr_n)
    df["chop"] = chop
    df["k_mult"] = k
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    df["supertrend"] = st["supertrend"]
    df["supertrend_dir"] = st["supertrend_dir"]
    return df
