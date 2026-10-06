# Funding Farm — 30d Historical Backtest Results

**Date:** 2026-10-06
**Method:** `scripts/backtest_funding.py --days 30 --top 20`
**Data:** real Hyperliquid `fundingHistory`, hourly walk, no lookahead
(universe = top 20 coins by 24h notional volume at backtest start).

## Headline

| metric | value |
|---|---|
| start equity | $10,000.00 |
| end equity | $10,016.50 |
| net PnL | **+$16.50 (+0.17%)** |
| implied APR | +2.0% |
| carry earned (closed + open) | +$197.17 |
| fees paid | $8.25 |
| ledger events | 8 |
| open positions at end | 2 |
| peak equity | $10,016.50 |

## Reading it honestly

- **The mechanism works:** the farm collected real carry (+$197 gross)
  with tiny fees ($8.25). The djienne switch rule kept churn near zero —
  only 8 events in 30 days, no over-trading.
- **The headline is understated by construction:** funding payments accrue
  to positions and are only realized into equity on close. $180 of the
  $197 carry sits in the 2 still-open positions at window end. Mark-to-market
  carry accounting would show roughly +1.9% for the month, not +0.17%.
  (Ledger improvement queued: accrue carry into equity hourly.)
- **Deployment was low:** max 2 coins × 25% cap = ≤50% of farm capital
  deployed. The +2.0% implied APR is on total farm capital; on deployed
  capital it is roughly double.
- **Regime caveat:** the last 30 days were a positive-funding regime for
  majors/alts. The design's kill criterion (sustained negative funding)
  was never tested. A bear-regime backtest is needed before any capital
  question.

## Verdict

Carry is real, costs are tiny, the switch rule behaves. Not yet a strategy
to fund: needs (1) mark-to-market carry accounting, (2) a bear-regime
backtest, (3) a 30-day live paper run. This stays paper-only.
