# Wyckoff Spring/Upthrust — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 50-bar range shakeouts, volume-confirmed
spring/upthrust entries, exits at the opposite range edge, 1xATR stop,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 211 | 18.5% | −$4,517 | −45.2% | −2.03 | −50.6% | −$21.41 | 0.72 |
| ETH | 153 | 24.2% | +$2,576 | +25.8% | +1.14 | −33.2% | +$16.84 | 1.15 |
| HYPE | 217 | 19.4% | −$2,935 | −29.3% | −1.24 | −45.1% | −$13.52 | 0.80 |
| **Combined** | **581** | **20.3%** | **−$4,876** | — | — | — | **−$8.39** | — |

## Verdict: mixed — ETH +25.8% on a 20% win rate is a lottery ticket

Springs on 1h crypto are mostly just breakdowns that keep breaking
down: the 18–24% win rate means four of five shakeouts are real
breakdowns, and the 1xATR stop can't save a system that is wrong that
often. ETH's +25.8% (Sharpe 1.14) comes from a handful of fat tails,
not from a reliable edge — the range100 variant keeps ETH positive
(+$832) but kills everything else. Wyckoff's schematics describe
multi-week accumulation; compressing them to 50 1h bars loses the
"cause" that the law of cause-and-effect requires.
