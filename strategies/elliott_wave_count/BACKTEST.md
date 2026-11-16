# Elliott Wave Count — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=100 bars.

## Results (shipped config: 5-bar pivots, wave-2 band 38.2–61.8%,
161.8% extension, 2xATR stop, 3xATR target, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 20 | 35.0% | +$58 | +0.6% | +0.24 | -3.0% | +$2.90 | 1.14 |
| ETH | 13 | 38.5% | -$160 | -1.6% | -0.69 | -2.1% | -$12.29 | 0.70 |
| HYPE | 1 | 100.0% | +$58 | +0.6% | +0.93 | -0.4% | +$57.76 | inf |
| **Combined** | **34** | **38.2%** | **-$44** | — | — | — | **-$1.29** | — |

The strict rules prune almost everything, exactly as the spec
warned: 36 entry signals in total (long entries 13/9/2, short
entries 8/4/0 for BTC/ETH/HYPE) become 34 trades. HYPE produced a
single trade in 8 months — one win, +$58, profit factor infinite on
a sample of one. Fees total $291 against a -$44 net.

## Verdict: break-even noise on a 34-trade sample — no conclusion possible

Combined -$44 with expectancy -$1.29/trade is indistinguishable
from zero, and with 34 trades it would stay indistinguishable from
zero if the sign flipped. BTC is marginally green (+$58, Sharpe
+0.24), ETH marginally red (-$160, Sharpe -0.69), HYPE is a single
data point. Nothing here is evidence for or against Elliott counting
as a signal — the strategy's honest output is that the strict count
almost never fires on 1h crypto, and when it does it pays about
nothing.

## Calibration note

Shipped the specified 5-bar pivots. A 3 – 5 – 7 pivot sweep is in
CALIBRATION.md: 3-bar pivots are clearly worse (-$1,365, BTC win
rate 17.9%, PF 0.11), 7-bar pivots are also ~breakeven (-$66, 45
trades). The shipped 5-bar setting is the least bad combined, but
that is an in-sample observation on 34–53 trades, not a
justification.

## Mechanism

Strict 5-bar pivots feed a latched state machine (idle → have wave 1
→ armed on a valid wave 2 → in wave 3 → in wave 5). Wave 2 must
retrace 38.2–61.8% of wave 1; entry is a close past the wave-1
extreme (wave-3 breakout). Wave 3 is checked against wave 1 when the
wave-4 pivot confirms; wave 4 must stay out of wave-1 territory; the
wave-5 target is the 161.8% extension of wave 1. 2xATR stop (≈ the
wave-2 extreme), 3xATR target, 96-bar max hold.

Source: Elliott Wave Theory —
https://www.rabofund.com/blogs/what-is-elliott-wave-theory-a-practical-guide-for-forex-traders

## Limitations

- 34 trades is far too thin for any statistical claim; the HYPE leg
  is a single trade.
- The 2xATR stop is an approximation of the textbook wave-2-extreme
  stop, not the literal level (see risk.py).
- The wave-3-shortest rule cannot be verified until wave 3 completes;
  the wave-5 target only exists after wave 4 confirms.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped pivot size on this window (see CALIBRATION.md).
