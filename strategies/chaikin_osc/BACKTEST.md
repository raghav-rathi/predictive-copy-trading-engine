# Chaikin Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: CHO = EMA3(ADL) − EMA10(ADL), zero-cross
entries, opposite-cross exits, 1.5xATR stop, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 616 | 27.9% | −$6,649 | −66.4% | −3.70 | −68.1% | −$10.79 | 0.67 |
| ETH | 652 | 29.4% | −$7,075 | −70.7% | −4.46 | −72.0% | −$10.85 | 0.64 |
| HYPE | 530 | 30.9% | −$2,332 | −23.2% | −0.86 | −27.9% | −$4.40 | 0.89 |
| **Combined** | **1,798** | **29.3%** | **−$16,056** | — | — | — | **−$8.93** | — |

## Verdict: loser everywhere (second-worst in batch)

The 3/10 EMA pair on the ADL is far too fast for 1h money flow — 1,798
trades of zero-line whipsaw, and the faster (2,6) variant is even worse
(−$22,667, 2,832 trades). Chaikin's oscillator was built to time
multi-week accumulation/distribution swings on dailies; at 1h the ADL's
CLV×volume term is dominated by intrabar close-location noise. The
slower (6,21) variant loses less but stays negative everywhere. Killed.
