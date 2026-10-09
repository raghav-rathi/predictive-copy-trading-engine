# Turtle Soup + Plus One — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 20-bar extremes, prior extreme >=4 bars old, 3-bar reclaim window)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 286 | 31.8% | -$4,544 | -45.4% | -3.75 | -45.6% | -$15.89 | 0.66 |
| ETH | 279 | 34.8% | -$3,727 | -37.3% | -2.73 | -41.9% | -$13.36 | 0.75 |
| HYPE | 278 | 30.6% | -$3,277 | -32.7% | -2.62 | -34.6% | -$11.79 | 0.75 |
| **Combined** | **843** | **32.4%** | **-$11,548** | — | — | — | -$13.70 | — |

## Verdict: LOSER (the worst fade in this batch)

Catastrophic on all three coins. The 3-bar reclaim window on 1h bars is far
too permissive: 843 trades means a "false breakout" signal roughly every 18
bars, and most reclaims are just noise oscillation around the level, not
trapped-trader squeezes. Fees alone ($7.5k combined) would sink it even if
the gross edge were flat — and the gross edge is negative (profit factor
0.66-0.75).

## Calibration note

Shipped the specified parameters exactly (20-bar extremes, >=4-bar-old
prior extreme, 3-bar reclaim window, 1.5xATR stop / 2.0xATR trail / 2.5xATR
target / 24-bar max hold) — no sweep, because the failure is not parametric:
the signal rate is 5-6x what a "rare trap" setup should produce. Raschke's
Turtle Soup is a daily-bar pattern where a 20-day extreme undercut is a
genuine positioning event; on 1h bars the 20-bar extreme is made and remade
constantly, so the "trap" has no trapped traders behind it. A daily-bar
re-test or a much stricter age/penetration filter might rescue the idea, but
the 1h port is dead on arrival. What held up in testing: the mechanics are
correct (signal -> reclaim within 3 bars verified, no lookahead), the
economics are not.

## Mechanism

Fade false breakouts: a new 20-bar low whose prior 20-bar low level is at
least 4 bars old, then a close back above the violated low within 3 bars
enters long (mirror for highs). Trade management: 1.5xATR stop, 2.0xATR
chandelier trail, 2.5xATR target, 24-bar max hold.

Source: Linda Raschke, Street Smarts (Turtle Soup) —
https://roboforex.com/blog/education/trading-strategies-that-were-a-revolution-three-strategies-of-linda-raschke/

## Limitations

- Single 7-month window; the pattern may behave differently on daily bars.
- Funding unmodeled.
- Next-bar-open execution vs idealized reclaim-close entry.
- No parameter sweep; the 1h timeframe choice is the prime suspect, not the params.
