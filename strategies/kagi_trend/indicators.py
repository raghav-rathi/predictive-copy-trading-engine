"""Kagi chart construction indicators.

Kagi charts ignore time and draw vertical price lines: a column extends
while price keeps moving the same way; when price reverses by at least
the reversal amount, a new column starts with a small horizontal step.

Reversal amount here = 4 x ATR(14) of the underlying 1h bars (the classic
Kagi "percentage/amount" parameter, volatility-scaled so one setting
works across BTC/ETH/HYPE).

Line thickness (yang/yin):
  * a rising column whose high exceeds the previous column's high grows
    a "shoulder" and the line thickens (yang = 1, bullish);
  * a falling column whose low undercuts the previous column's low makes
    a "waist" and the line thins (yin = 0, bearish).

Columns per bar (forward-filled while no new column forms):
  kagi_dir    -- +1 (rising column) / -1 (falling column)
  kagi_thick  -- True (yang) / False (yin)
  kagi_extreme -- current column's extreme (top when rising, bottom falling)
  kagi_rev    -- reversal amount used on that bar

No lookahead: the column state on bar i uses closes and ATR through i
only. (Using close-based kagi rather than high/low-based: high/low
kagi would peek at intrabar range after the close is known -- closes
keep the no-lookahead contract clean.)
"""

import numpy as np
import pandas as pd

from strategies import base as B

REV_ATR_MULT = 4.0
ATR_N = 14


def _build_kagi(closes: np.ndarray, rev: np.ndarray) -> tuple:
    """Single numpy loop over bars. Returns (kdir, kthick, kextreme)."""
    n = len(closes)
    kdir = np.full(n, np.nan)
    kthick = np.full(n, np.nan)
    kext = np.full(n, np.nan)
    if n < 2:
        return kdir, kthick, kext
    valid = np.where(np.isfinite(rev) & (rev > 0))[0]
    if len(valid) == 0:
        return kdir, kthick, kext
    seed = max(int(valid[0]), 1)
    # seed the first column from the first two closes
    d = 1 if closes[seed] >= closes[seed - 1] else -1
    base = closes[seed - 1]          # origin of the current column
    top = max(closes[seed - 1], closes[seed])
    bot = min(closes[seed - 1], closes[seed])
    prev_high, prev_low = top, bot   # extremes of previous completed column
    thick = False
    for i in range(seed, n):
        ci = closes[i]
        r = rev[i]
        if np.isfinite(r) and r > 0:
            if d == 1:
                if ci >= top:
                    top = ci
                elif top - ci >= r:
                    # reversal: new falling column, horizontal step at `top`
                    prev_high, prev_low = top, base
                    d, base, bot = -1, top, ci
                    if bot < prev_low:        # waist: breaks prior column low
                        thick = False
            else:
                if ci <= bot:
                    bot = ci
                elif ci - bot >= r:
                    # reversal: new rising column, horizontal step at `bot`
                    prev_high, prev_low = base, bot
                    d, base, top = 1, bot, ci
                    if top > prev_high:       # shoulder: breaks prior column high
                        thick = True
            # mid-column thickening/thinning as extremes break the prior column
            if d == 1 and top > prev_high:
                thick = True
            elif d == -1 and bot < prev_low:
                thick = False
        kdir[i] = d
        kthick[i] = thick
        kext[i] = top if d == 1 else bot
    return kdir, kthick, kext


def add_indicators(
    df: pd.DataFrame,
    rev_mult: float = REV_ATR_MULT,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    closes = df["c"].to_numpy(dtype=float)
    rev = (rev_mult * B.atr(df["h"], df["l"], df["c"], atr_n)).to_numpy()
    kdir, kthick, kext = _build_kagi(closes, rev)
    df["kagi_dir"] = pd.Series(kdir).ffill().fillna(1.0)
    df["kagi_thick"] = pd.Series(kthick).ffill().fillna(False).astype(bool)
    df["kagi_extreme"] = pd.Series(kext).ffill()
    df["kagi_rev"] = rev
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
