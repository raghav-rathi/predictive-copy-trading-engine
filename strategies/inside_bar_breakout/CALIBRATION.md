# Inside Bar Breakout — Calibration

**Everything here is fixed a priori from the price-action canon;
no parameter sweep was run and none is planned on this window.**

- **Strict inside definition** — `h < h.shift(1)` and
  `l > l.shift(1)`: the whole bar inside the mother bar. The
  sources describe the inside bar as the child bar contained
  within the mother bar's range; the strict variant (wick poking
  out disqualifies) is the common mechanical implementation.
- **5-bar expiry** — the canon treats the inside bar as a
  short-lived compression: if price doesn't break out within a
  few bars the setup is stale. 5 bars is the conventional
  mechanical choice; a longer window would let dead setups
  linger, a shorter one would strangle real breakouts.
- **Tie-break by mother direction** — on a same-bar double cross
  the mother bar's direction resolves the ambiguity (bull mother
  → long); this is a pure rule-completeness choice, not a tuned
  one.
- **1.5xATR stop, 2R target, 48-bar max hold** — the canon stop
  sits on the opposite side of the mother bar and the target is
  2:1 minimum; the ATR parametrizations and the ~2-day max hold
  are the harness's standard translations.

Deliberately not swept: the expiry window (5), the strictness of
the inside definition, and the 2R target. Sweeping them on the
backtest window would be in-sample selection, and the result
(BACKTEST.md) is a decisive loser — tuning a 37%-win-rate churn
system's expiry by ±2 bars is rearranging deck chairs, not
finding an edge. Any future work on this pattern belongs on
walk-forward data and different timeframes (the daily inside bar
is the canon's home turf; the 1h may simply be too noisy).
