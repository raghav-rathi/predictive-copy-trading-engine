# Ease of Movement — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: EMV(14) zero-cross entries, opposite-cross
exits, 2xATR stop, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 606 | 27.6% | −$4,984 | −49.5% | −2.93 | −60.3% | −$8.22 | 0.71 |
| ETH | 618 | 25.4% | −$5,949 | −57.6% | −3.59 | −61.9% | −$9.63 | 0.64 |
| HYPE | 536 | 31.3% | −$1,410 | −13.2% | −0.53 | −26.0% | −$2.63 | 0.92 |
| **Combined** | **1,760** | **28.0%** | **−$12,343** | — | — | — | **−$7.01** | — |

## Verdict: loser everywhere

Arms' zero-cross is a daily-chart concept; on 1h crypto the 14-bar EMV
spends most of its time whipsawing across zero (1,760 trades). Even the
slower EMV(28) variant stays negative on all three coins. The indicator
measures how "easily" price moves, but ease of movement on 1h bars is
dominated by bar-to-bar noise, not by the accumulation/distribution
Arms designed it for. Killed.
