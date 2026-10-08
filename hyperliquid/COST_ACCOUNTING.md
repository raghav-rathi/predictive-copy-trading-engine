# Cost accounting in the copy book (2026-10-08)

STRATEGY_RESEARCH.md ideas 4a + 5, built 2026-10-08.

## What changed

The engine's paper ledger (`hyperliquid/paper.py`) previously modeled
**zero** exchange fees and **zero** funding payments, and the backtest
assumed a 0.035% taker fee that sits *below* the documented 0.045%
base rate. Both are now modeled, paper-first:

- `hyperliquid/costs.py` — `taker_fee_rate()` resolves the real
  tiered taker fee from the public `userFees` endpoint when a
  `costs.account` address is configured, else falls back to the
  documented base schedule (0.045% taker / 0.015% maker, verified live
  2026-10-08). `FundingLedger` accrues hourly funding from public
  `fundingHistory`, signed (positive rate => longs pay shorts), with
  partial-hour pro-rating, per-(coin,hour) caching, and failed fetches
  recorded as gaps (accrued 0.0, never silently).
- `paper.py` close paths now write `fees_usd` and `funding_usd`
  columns and fold both into `pnl_usd` (price PnL − fees ± funding).
  Applies to real closes and shadow closes. Optional
  `hyperliquid.costs` config section: `{account, funding_accounting}`;
  defaults keep the ledger working with no config change.
- `hyperliquid/tests/test_costs.py` — 19/19 green: sign conventions,
  pro-rating, cache dedup, failure fallbacks, userFees parsing.

## Empirical validation (live paper test, 2026-10-02 → 10-08)

`scripts/funding_impact.py` (read-only) reconstructed 142 closed legs
from the live paper test's fill log and accrued real funding:

| metric | total | per leg |
|---|---|---|
| realized PnL (tracker, net of modeled 0.035% fees) | +$2.70 | +$0.0190 |
| funding PnL (real history) | −$0.65 | −$0.0046 |
| extra fees at real 0.045% tier vs assumed | −$2.07 | −$0.0146 |
| **honest total** | **−$0.03** | |

Funding drag sits almost entirely on longs (−$0.64 of −$0.65),
consistent with funding positive ~99% of hours. Shorts netted ≈$0.

## Implication

The headline paper edge (~$0.019/leg) does not survive honest cost
accounting — this is the dropstab follower-bleed mechanism in our own
data (48% of followers profitable vs 97% of leaders across 100k copy
trades: the signal isn't the problem, execution cost is). This does
not change strategy selection by itself, but it changes calibration:
any future call/backtest comparison must use cost-honest PnL, and
idea 1 (maker/post-only entries, 3x fee gap) is now the highest-EV
open item on the core book — the fill-rate experiment is the next
build that can actually move this number.
