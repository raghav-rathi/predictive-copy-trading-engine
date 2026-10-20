"""Ross Hook entry signals.

Bullish sequence (mechanical 1-2-3 + hook):

  P1: pivot low
  P2: pivot high after P1
  P3: pivot low after P2 with P3 price > P1 price (higher low)
  breakout: a close above P2
  hook: after the breakout, a pivot high that stays above P3
  long_entry: close above the hook high

Bearish: mirror image (P1 pivot high, P2 pivot low after P1, P3 pivot
high after P2 with P3 < P1, breakdown = close below P2, hook = pivot
low after the breakdown staying below P3, short_entry = close below the
hook low).

Invalidation: after the 1-2-3 completes, a close back through P1
(bullish) / P1 (bearish) resets the sequence. After an entry fires, the
sequence resets so the engine waits for a fresh pattern.

The harness handles execution at next-bar open plus the 1.5xATR stop
(stop below the hook low is approximated by the ATR stop), the
2.5xATR target, and the 60-bar max hold. Exits are the opposite
sequence's entry (structural flip).

No lookahead: pivots enter the loop only when their full window is
confirmed (see indicators), and decisions at bar j use closes <= j.
"""

import numpy as np
import pandas as pd


class _Seq:
    """One directional 1-2-3+hook tracker."""

    def __init__(self, bullish: bool):
        self.bullish = bullish
        self.reset()

    def reset(self):
        self.p1 = None  # (idx, price)
        self.p2 = None
        self.p3 = None
        self.broken = False
        self.hook = None  # (idx, price)

    def _new_pivot(self, idx, price, is_high):
        b = self.bullish
        if b:
            if not is_high:  # pivot low
                if self.p1 is None:
                    self.p1 = (idx, price)
                elif self.p2 is None:
                    if price < self.p1[1]:
                        self.p1 = (idx, price)  # lower low: restart
                elif self.p3 is None:
                    if price > self.p1[1]:
                        self.p3 = (idx, price)
                    else:  # lower low: restart the sequence
                        self.reset()
                        self.p1 = (idx, price)
                # pivot lows after the hook is armed are ignored
            else:  # pivot high
                if self.p1 is not None and self.p2 is None:
                    self.p2 = (idx, price)
                elif self.broken and self.hook is None and self.p3 is not None \
                        and idx > self.p2[0] and price > self.p3[1]:
                    self.hook = (idx, price)
        else:
            if is_high:  # pivot high
                if self.p1 is None:
                    self.p1 = (idx, price)
                elif self.p2 is None:
                    if price > self.p1[1]:
                        self.p1 = (idx, price)  # higher high: restart
                elif self.p3 is None:
                    if price < self.p1[1]:
                        self.p3 = (idx, price)
                    else:  # higher high: restart the sequence
                        self.reset()
                        self.p1 = (idx, price)
            else:  # pivot low
                if self.p1 is not None and self.p2 is None:
                    self.p2 = (idx, price)
                elif self.broken and self.hook is None and self.p3 is not None \
                        and idx > self.p2[0] and price < self.p3[1]:
                    self.hook = (idx, price)

    def on_bar(self, j, close, piv_high, piv_high_px, piv_low, piv_low_px):
        """Process bar j. Returns 'long' / 'short' / None."""
        b = self.bullish
        if piv_high and np.isfinite(piv_high_px):
            self._new_pivot(j, piv_high_px, True)
        if piv_low and np.isfinite(piv_low_px):
            self._new_pivot(j, piv_low_px, False)

        p1, p2, p3 = self.p1, self.p2, self.p3
        if b:
            if p1 is not None and p2 is not None and p3 is not None:
                if not self.broken and close > p2[1]:
                    self.broken = True
                if self.broken and self.hook is not None and close > self.hook[1]:
                    self.reset()
                    return "long"
                if close < p1[1]:  # pattern invalidated
                    self.reset()
        else:
            if p1 is not None and p2 is not None and p3 is not None:
                if not self.broken and close < p2[1]:
                    self.broken = True
                if self.broken and self.hook is not None and close < self.hook[1]:
                    self.reset()
                    return "short"
                if close > p1[1]:  # pattern invalidated
                    self.reset()
        return None


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    ph = df["piv_high"].to_numpy(dtype=bool)
    ph_px = df["piv_high_px"].to_numpy(dtype=float)
    pl = df["piv_low"].to_numpy(dtype=bool)
    pl_px = df["piv_low_px"].to_numpy(dtype=float)

    bull = _Seq(bullish=True)
    bear = _Seq(bullish=False)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    for j in range(n):
        if bull.on_bar(j, c[j], ph[j], ph_px[j], pl[j], pl_px[j]) == "long":
            long_entry[j] = True
        if bear.on_bar(j, c[j], ph[j], ph_px[j], pl[j], pl_px[j]) == "short":
            short_entry[j] = True

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = df["short_entry"].astype(bool)
    df["short_exit"] = df["long_entry"].astype(bool)
    return df
