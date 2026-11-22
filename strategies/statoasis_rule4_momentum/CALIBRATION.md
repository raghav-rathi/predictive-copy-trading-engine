# StatOasis Rule 4 — Calibration

All parameters were fixed **a priori** from the published
StatOasis Rule 4 specification (verbatim from the article's
Finding 4 table) and the 1d → 1h adaptation — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| RSI threshold | 14, > 55 long / < 45 short | source spec, verbatim (short threshold mirrors the long one around 50) |
| Stochastic %K | 14, smooth 3, > 50 long / < 50 short | source spec, verbatim; %K is the 3-bar SMA of raw %K |
| Williams %R | 14, > −50 long / < −50 short | source spec, verbatim |
| Return filter | 120h return > 1% long / < −1% short | source's 5-day return, adapted to 1h bars (5 days = 120h) |
| Time exit | 10 bars | source's 10-bar hold, adapted to 10 hours |
| ATR window | 14 | canonical |
| Stop | 2xATR | roomy catastrophic protection; the source has no stop at all |
| Trail / target | none / none | trailing would fight the fixed-hold thesis; the source has neither |
| Max hold | 10 bars | enforces the time exit in the harness as well as in signals.py |
| Risk | 1% / trade, 3x leverage cap | house standard |

## Documented deviations from the source

1. **Timeframe: daily SPY → 1h crypto.** The source is a daily
   rule on SPY (5-day return, 10-day hold). Adapted per the
   brief: 5-day return → 120h return, 10-bar hold → 10h. The
   oscillator lookbacks (14) are unchanged in bars, which
   means they now span 14 hours instead of 14 days — a much
   faster, noisier filter. This adaptation is the most likely
   reason the result does not transfer (see BACKTEST.md).
2. **Short side is a builder-added mirror.** The source rule is
   long-only. The short mirror (RSI < 45, %K < 50, %R < −50,
   return < −1%) is symmetric around the 50 / −50 midpoints
   and was not tested by StatOasis.
3. **A stop was added.** The source has no stop and no
   indicator exit — only the time exit — and its test was
   frictionless. A 2xATR stop was added as catastrophic
   protection for leveraged crypto; it fires often and changes
   the tested object (see BACKTEST.md). Removing it would be
   more faithful but would leave leveraged positions with no
   downside bound, which the harness does not support.
4. **Costs are real here, frictionless there.** The source test
   had no commissions or slippage; this run charges 0.045%
   taker + 0.01% slippage per side. On a 10-bar hold with
   ~1,000 trades, that cost dominates the result.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers.
