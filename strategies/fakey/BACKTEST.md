# Fakey — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only via the pinned batch-45 runner
(`scripts/run_pinned_backtest45.py`), window ms
`[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC exclusive; last bar 2026-11-24 13:00 UTC):
6,111 bars BTC/ETH, 6,109 HYPE (first HYPE bar 2026-03-15
00:00 UTC). Batch 45 refresh of the Nov-14 build; the stale
Nov-14 window numbers have been replaced, not kept alongside.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start per coin. WARMUP=5 bars.

## Results (shipped config: mother-bar confirmation — close back
inside the mother bar's range; long on false downside break,
short on false upside break, exits on the opposite signal, 2xATR
stop, 3xATR trail, 60-bar max hold)

| Coin | Bars | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 6,111 | 383 | 40.47% | -$3,968.86 | -39.68% | -2.60 | -46.53% | -$10.36 | 0.68 | $2,850.48 |
| ETH | 6,111 | 421 | 40.14% | -$2,897.39 | -28.97% | -1.59 | -36.50% | -$6.88 | 0.82 | $2,855.87 |
| HYPE | 6,109 | 331 | 38.67% | -$2,567.75 | -26.17% | -1.65 | -31.86% | -$7.76 | 0.83 | $1,483.41 |
| **Combined** | **18,331** | **1,135** | **39.82%** | **-$9,434.01** | — | — | — | **-$8.31** | — | **$7,189.76** |

## Verdict: loser on all three coins — the pattern fires, the trap doesn't pay

Negative everywhere: combined -$9,434.01 on 1,135 trades, win
rate 39.82%, profit factor 0.68–0.83 on every coin. The fakey
premise does not pay on 1h crypto: the false break is
identified as designed, but the "trapped breakout traders fuel
the reversal" story does not follow — entries bleed straight
into the 2xATR stop (expectancy -$6.88 to -$10.36 per trade,
among the worst per-trade losses in this batch) and the
opposite-signal exit closes whatever is left. MaxDD -32% to
-47% on every coin.

The losses are structural, not cost-driven: gross of fees the
book is still -$2,244.25 (BTC -$1,118.38, ETH -$41.53,
HYPE -$1,084.34) — i.e. the signal itself is negative-edge
before costs, and $7,189.76 of fees make it worse. Unlike the
crossover strategies in this batch, no fee adjustment rescues
this one. The extra 10 days of data vs the Nov-14 run made it
worse (-$9,434.01 vs -$8,714), not better.

## Calibration note

Shipped the specified mother-bar confirmation. A mother-range
vs inside-range confirmation sweep is in CALIBRATION.md: the
stricter inside-range confirmation is less bad combined
(-$7,103.50 vs -$9,434.01) and much less bad on ETH (-$939.66
vs -$2,897.39), but still negative on every coin and worse on
HYPE (-$3,298.59). The confirmation range is not the problem
— a 3-bar pattern on 1h crypto is mostly noise. The mother
confirmation was fixed before any backtest was run; no
in-sample adoption.

## Audit (batch 45 refresh)

All 8 files re-read and re-verified on the batch-45 window. No
lookahead found: `is_inside` compares bar i to bar i-1 only;
the signal conditions use only shifts of 1–2 bars (mother,
inside, break bar) and bar i's own close. NaN handling is
explicit (`.fillna(False)` on every signal column; boolean
dtype enforced). The both-sides-break ambiguity guard (a
wide-range bar breaking both inside extremes fires neither
entry) is intact and covered by test. No bug found, no code
changed in this refresh — parameters untouched.

## Mechanism

Nial Fuller Fakey: mother bar i-2; inside bar i-1 (high <
mother high AND low > mother low). Bullish fakey: bar i breaks
below the inside bar's low (low[i] < low[i-1]) but closes back
inside the mother bar's range (close[i] > low[i-2]) → long.
Bearish fakey: bar i breaks above the inside bar's high
(high[i] > high[i-1]) but closes back inside the mother bar's
range (close[i] < high[i-2]) → short. A bar breaking both sides
while closing inside the mother range fires neither entry
(ambiguous). Exit on the opposite signal. 2xATR hard stop,
3xATR chandelier trail, 60-bar max hold.

Source: Nial Fuller, Fakey pattern —
https://www.learntotradethemarket.com/forex-trading-strategies/what-is-fakey-pattern

## Limitations

- Single 8.5-month crypto window; 1,135 trades is a decent
  sample and the verdict is consistent across coins, so this is
  not a small-sample artifact.
- 39.82% win rate with PF < 0.9 on all three coins — the edge
  is negative gross of fees; no confirmation tweak rescues it
  (see CALIBRATION.md).
- The pattern is a 3-bar discretionary chart pattern forced
  into a mechanical rule: no trend filter, no volume filter, no
  location filter (key level, trend context) — the textbook
  pattern is always traded at support/resistance, which this
  engine ignores by design.
- Funding unmodeled; next-bar-open execution vs idealized entry.
