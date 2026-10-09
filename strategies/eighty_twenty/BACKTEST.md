# 80-20 Momentum-Candle Fade — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 80th-pct 20-bar range, 0.5xATR push, 5-bar window, 1.5xATR target)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 418 | 57.2% | -$2,851 | -28.5% | -2.26 | -32.4% | -$6.82 | 0.84 |
| ETH | 443 | 51.9% | -$5,266 | -52.6% | -4.55 | -56.6% | -$11.89 | 0.67 |
| HYPE | 396 | 52.5% | -$3,872 | -38.7% | -3.16 | -44.4% | -$9.78 | 0.76 |
| **Combined** | **1257** | **53.9%** | **-$11,989** | — | — | — | -$9.54 | — |

## Verdict: LOSER

The cruelest profile in the batch: a 52-57% win rate that still loses
$12k. The fade wins small and loses big — when the push is genuine
momentum continuation rather than exhaustion, the 2xATR stop takes the
full loss while winners are capped at the 1.5xATR target. 1,257 trades also
means $8.4k in combined fees: the 80th-percentile bar filter fires far too
often on 1h crypto bars to be the "rare exhaustion candle" Raschke
describes.

## Calibration note

Shipped the specified parameters exactly (80th percentile of trailing-20
ranges, >=0.5xATR push past the momentum close, close back inside the
momentum [low, high] within 5 bars, 1.5xATR target / 2xATR stop / 24-bar
max hold). One implementation deviation from the naive reading, kept
deliberately: push detection runs on every bar with active momentum levels
(including chained momentum bars, which re-anchor the levels) rather than
only non-momentum bars — otherwise consecutive momentum bars erase the
push memory and the setup can never complete. Entries are still barred
from momentum bars themselves. This does not change the verdict: the
problem is the payoff asymmetry (capped winners, full-size losers) and the
signal rate, not the push accounting.

## Mechanism

After an 80th-percentile-range momentum candle, if price pushes >=0.5xATR
beyond the momentum close and then closes back inside the momentum bar's
[low, high] within 5 bars, fade it (up-momentum -> short, down-momentum ->
long). Exit: 1.5xATR target, 2xATR stop, 24-bar max hold.

Source: Linda Raschke, Street Smarts (80-20) —
https://roboforex.com/blog/education/trading-strategies-that-were-a-revolution-three-strategies-of-linda-raschke/

## Limitations

- Single 7-month window; daily-bar 80-20 (Raschke's native timeframe) untested.
- Funding unmodeled.
- Next-bar-open execution vs idealized fade entry.
- Win-rate/target asymmetry suggests the target/stop ratio, not just the signal, needs work.
