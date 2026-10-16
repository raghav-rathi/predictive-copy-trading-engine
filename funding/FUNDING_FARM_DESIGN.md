# Delta-Neutral Funding Farm — Design

**Date:** 2026-10-06
**Status:** design, pre-backtest
**Track:** second uncorrelated book next to the directional copy engine

## Thesis

Hyperliquid funding is positive ~99% of hours on majors (BTC +0.00119%/hr ≈
10.4% APR, ETH 10.6%, SOL 8.6% measured over 60d by IvPalmer/Master-Trader).
A portfolio that is **1x short perp + 1x long spot** on the highest-funding
coins harvests that carry while staying price-neutral. This is yield (8–15%
APY), not alpha — it diversifies the copy book, it does not 10x.

Prior art: djienne/delta_neutral_hyperliquid_perp_spot (2 years of funding
history calibrated, switches only when expected gain beats 4-leg costs, ~12
APY-point gap); Harmonix USDC-HYPE delta-neutral vault live at 8–15% APY;
Pendle Boros productizing cross-exchange funding arb.

## Mechanics

1. **Hourly scan.** Pull current funding for every perp via `metaAndAssetCtxs`
   (asset ctx `funding` field = hourly rate, fractions of 1, e.g. 0.0000125).
2. **Rank by 7-day average.** Hourly funding is noisy; rank coins on the
   trailing 168-hour mean from `fundingHistory`. Positive sign = longs pay
   shorts, so we short the perp.
3. **Enter.** Top 1–2 coins whose 7d avg clears the entry threshold
   (default 0.0008%/hr ≈ 7% APR). Legs: short perp via the engine's execution
   path + long spot (1x, same notional) to stay delta-neutral.
4. **Switch.** Re-rank hourly. Move capital to a new candidate only when
   `(candidate_7d_avg − held_7d_avg) × horizon_hours > 4-leg round-trip cost`
   (default horizon 168h, costs = 2× taker + 2× spot fee + slippage buffer).
   This is the djienne rule: churn only when the carry gain pays the switch.
5. **Exit.** Close both legs when the held coin's 7d avg turns negative
   (funding regime flip) or the position ages past the max hold (default 30d,
   forces a re-rank).

## Sizing

- Book cap: configurable fraction of paper equity (default 25% of the farm's
  allocated capital per coin, max 2 coins → ≤50% of farm capital deployed).
- Per-coin notional: `min(max_notional, farm_capital × weight)` where weight
  is proportional to the coin's 7d avg funding (carry-weighted, not
  equal-weight — money should sit where carry is highest).
- Leverage: none beyond 1x per leg (delta-neutral by construction).

## Costs modeled

- Perp entry/exit: taker 0.035% per leg (conservative vs 0.045% base).
- Spot entry/exit: 0.02% per leg estimate.
- Funding payments: hourly, signed (short collects positive funding).
- No borrow cost modeled for spot long (assumes spot balance, not margin).

## Risks (kill criteria)

1. **Funding regime flip.** Sustained bear → negative funding → the farm
   bleeds. Guardrail: global pause if portfolio 7d realized carry < 0.
2. **Basis risk.** Perp/spot can diverge intraday; 1x sizing bounds it, but
   mark-to-market swings hit the paper equity curve.
3. **Execution complexity.** Two legs, two venues of failure; paper-mode
   first, 30 days minimum, before any capital question.
4. **Thin funding history.** New listings have <168h of funding history;
   require ≥72h of history before a coin is rankable.

## What this track will NOT do

- No leverage, no directional view, no cross-exchange legs (single-venue HL
  only — cross-venue is research idea #7, separate track).
- Not wired into the live copy engine. Paper-only until the backtest and a
  30-day paper run both clear review.
