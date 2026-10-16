# Ultimate Oscillator divergence — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: UO(7/14/28), k=3 fractal pivots, regular
divergence within a 120-bar window, UO<30 / UO>50 confirmation dips,
exits at UO>70 / UO<30, 2xATR stop, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 64 | 18.8% | −$1,897 | −19.1% | −1.78 | −30.6% | −$29.64 | 0.66 |
| ETH | 65 | 20.0% | −$1,577 | −9.2% | −0.58 | −31.4% | −$24.26 | 0.72 |
| HYPE | 60 | 26.7% | −$758 | −7.6% | −0.57 | −19.9% | −$12.63 | 0.82 |
| **Combined** | **189** | **21.7%** | **−$4,232** | — | — | — | **−$22.39** | — |

## Verdict: honest loser on all three coins

Divergences on 1h crypto fire more often than the textbook suggests
(~60 per coin over the window — the k=3 fractal is a generous pivot
detector) and win under 27% of the time. The pattern is consistent:
momentum divergence marks a pause, not a reversal, on hourly crypto —
price consolidates and then continues, stopping out the counter-trend
entry. The UO>70/UO<30 exits rarely get to do their job because the
2xATR stop usually fires first.

Note on trade count: 60–65 trades is higher than "textbook rare"
because a 3-bar fractal on noisy hourly data finds pivots everywhere;
the divergence conditions filter most of them, but plenty remain.
Tightening the pivot to k=5 cuts trades ~15% and loses slightly more —
the problem is the premise, not the parameters. No variant earns
promotion. This one stays in the library as a documented negative
result.
