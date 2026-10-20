# Ross Hook Continuation — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,276 bars BTC/ETH, 5,274 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: 5-bar fractal pivots, 1.5xATR stop,
2.5xATR target, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 109 | 39.4% | -$709 | -7.1% | -0.51 | -17.7% | -$6.50 | 0.90 |
| ETH | 99 | 30.3% | -$2,452 | -24.5% | -2.64 | -26.4% | -$24.77 | 0.63 |
| HYPE | 119 | 37.0% | -$760 | -7.6% | -0.62 | -14.6% | -$6.39 | 0.90 |
| **Combined** | **327** | **35.8%** | **-$3,921** | — | — | — | -$11.99 | — |

## Verdict: loser — the hook keeps failing on 1h crypto

327 trades, negative on all three coins, worst on ETH (PF 0.63, Sharpe
-2.64, max drawdown -26.4%). The pattern's logic — buy the first
pullback after a genuine 1-2-3 breakout — sounds right, but on 1h
crypto the "hook" pivot high is more often a local top before a deeper
retest than a launchpad: breakouts that trigger the entry frequently
roll over and take the 1.5xATR stop. BTC and HYPE are only mildly
negative (PF 0.90 each), so this is not a blowout — but with fees
($3,029 combined) the expectancy is -$12/trade and there is no coin
where it works. Honest read: the mechanical pivot simplification may be
firing on too many low-quality 1-2-3s (Ross's discretionary version
filters by trend context and bar character, which this engine does
not).

## Calibration note

Shipped the specified 5-bar pivots. A 3/5/7-bar pivot sweep is in
CALIBRATION.md: no setting is positive combined (-$3,821 / -$3,921 /
-$4,163); 3-bar pivots are least bad on BTC (-$327, PF 0.97) and 7-bar
worst almost everywhere. Pivot length moves the trade count (487 → 327
→ 234) more than the edge. Keep 5 bars as specified; nothing in the
sweep earns adoption.

## Mechanism

5-bar fractal pivots (2-bar confirmation shift, no lookahead). Bullish:
pivot low P1, pivot high P2 after P1, pivot low P3 after P2 with
P3 > P1; breakout = close above P2; hook = first pivot high after the
breakout that stays above P3; long on a close above the hook high.
Bearish mirror. A close back through P1 invalidates the sequence; the
sequence resets after each entry. Documented simplification of Ross's
discretionary pattern.

Source: Ross Hook (Joe Ross, via theforexgeek.com) —
https://theforexgeek.com/ross-hook-pattern/

## Limitations

- Single 7-month crypto window; 327 trades is a reasonable but not
  large sample.
- The pivot simplification drops Ross's discretionary filters (trend
  context, bar character, "point 2 must be a clear swing") — likely a
  source of low-quality setups.
- The 1.5xATR stop is a proxy for "below the hook low", not the actual
  hook low; a structure-based stop might behave differently.
- Funding unmodeled; next-bar-open execution vs idealized entry.
