# Tuning experiment — copy-engine backtest variants (2026-10-02)

Baseline 30d backtest was flat (+$4.84 net, 775 trades, 51.5% WR) with two
suspected drags: (1) the 2% trailing stop (dominant independent exit,
179/775 legs — hypothesized to cut winners short); (2) over-conservative
Kelly sizing ($21–49 positions vs $200 base). Three variants rerun over the
same ~30d window, same 4 vaults, same costs (0.035% taker + 0.02% slippage
per side), same gate (score ≥ 65, ≥ 10 closes).

## Configurations

| Run | Trailing | Kelly fraction | Note |
|-----|----------|----------------|------|
| BASE | 2% on | 0.25 | original backtest.py, untouched |
| A | OFF | 0.25 | tests the trailing-stop hypothesis |
| B | OFF | 0.50 | A + looser Kelly (linear cap scale; skip-on-negative-edge kept) |
| C | 2% on | 0.50 | extra isolation run: Kelly effect with baseline exits |

Kelly 0.5 chosen over lowering the edge floor: it directly addresses
starved sizes without touching the skip logic.

## Results (paper legs only)

| Run | Trades | Net PnL | WR | Fees | Avg/trade | Top-3 share of net | Net ex-top-3 |
|-----|--------|---------|----|------|-----------|--------------------|--------------|
| BASE | 775 | +$4.84 | 51.5% | $22.52 | +$0.006 | +$40.71 (842%) | −$35.88 |
| A | 978 | −$179.71 | 46.5% | $17.58 | −$0.184 | +$56.61 (−32%) | −$236.32 |
| B | 1,559 | −$171.06 | 49.9% | $22.77 | −$0.110 | +$63.54 (−37%) | −$234.60 |
| C | 1,335 | +$34.55 | 51.3% | $30.20 | +$0.026 | +$42.95 (124%) | −$8.40 |

Per-vault net (C, the best run): winning-fortunes +$16.37 (197 trades),
GeorgV Copytrading +$22.85 (72), Kairos Fi −$4.67 (1,066), Aquila $0
(all 8 intents skipped by gate/Kelly).

Exit mix (C): target_exit 1,097 / trailing 202 / maxhold 17 / stop 8.
Exit mix (A, no trailing): target_exit 846 / stop 36 / maxhold 83 / tp 6 —
positions that would have trailed out instead rode to target exits or
the 24h cap, and usually did worse there.

## Verdicts on the two hypotheses

1. **Trailing-stop hypothesis: REFUTED.** Removing it (A) turned +$4.84
   into −$179.71 with broad-based losses (ex-top-3 −$236). The trailing
   stop was protective, not harmful — it was cutting losers short, not
   winners. The original inference came from shadow signals that used
   *different exits and different sizing*, so it did not transfer.
2. **Kelly hypothesis: PARTIALLY CONFIRMED, small effect.** With exits
   held at baseline, Kelly 0.5 (C: +$34.55) beats Kelly 0.25 (BASE:
   +$4.84) by ~$30. Directionally right, not game-changing.

## Honest bottom line

**No variant shows real, robust edge.** The best config (C) makes +$34.55
(+0.35% on $10k / 30d) — and 124% of that is the top-3 trades; ex-top-3
it is −$8.40. The typical copied trade earns ~$0.03 against ~$0.11+
round-trip costs: gross edge per trade is ~zero, so results are
outlier-driven in every run. Tuning moved the needle +$5 → +$35 but did
not create edge; further parameter fiddling on 30 days risks overfitting.

What IS validated (again): the score gate. Rejected-signal shadows lost
money in all four runs (−$1,449 / −$1,528 / −$518 / −$645). The gate
keeps the strategy out of losers; the missing piece is positive edge on
the entries it accepts — copying at the target's fill price with full
taker + slippage leaves no margin on the typical trade.

## What would actually change the economics (not tested)

- Tighter gate (e.g. score ≥ 75) or fewer, higher-conviction vaults —
  fewer trades, only the strongest signals.
- Cheaper execution (maker/IOC placement instead of taker fills) — hard
  to reconcile with copy latency.
- Accept the finding: these vaults' edge does not survive copy frictions
  as configured; the forward paper test (running as control) is the
  out-of-sample check.

## Files

- `backtest_tuned.py` — parameterized copy of backtest.py
  (VARIANT=A/B/C, TRAILING_ENABLED, KELLY_FRACTION env knobs). Baseline
  `backtest.py`, `backtest_summary.json`, `backtest_trades.csv`,
  `paper_tracker.*` untouched.
- `backtest_tuned_{A,B,C}_summary.json` / `backtest_tuned_{A,B,C}_trades.csv`
- `backtest_tuned.log`
