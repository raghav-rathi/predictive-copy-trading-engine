# Keltner Channel + RSI — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to t >= 1773525600000:
BTC/ETH 5,445 bars, 2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC;
HYPE 5,443 bars, 2026-03-15 00:00 UTC → 2026-10-27 13:00 UTC.
**Window:** 2026-03-14 → 2026-10-27, Hyperliquid 1h, $10k, 1% risk, 3x cap, 0.045% fee + 0.01% slippage/side, funding off.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage
cap, $10k start, long/short. Funding not modeled (fully offline run).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 223 | 30.5% | -2,852 | -28.5% | -2.05 | -31.9% | -12.79 | 0.72 |
| ETH | 223 | 31.4% | -2,284 | -22.8% | -1.55 | -27.5% | -10.24 | 0.78 |
| HYPE | 214 | 34.1% | -529 | -5.3% | -0.24 | -14.2% | -2.47 | 0.95 |
| **Combined** | **660** | — | **-5,665** | — | — | — | **-8.58** | — |

Total fees: $4,876.

## Verdict

LOSER on all three legs. Combined −$5,665 across 660 trades (−$8.58 expectancy, the worst per-trade expectancy in the batch). BTC −$2,852 (Sharpe −2.05) and ETH −$2,284 lead the losses; even HYPE loses. The RSI filter trims the worst blow-offs (verified in tests: an overbought breakout is blocked) but the remaining breakouts still mean-revert more often than they follow through. Channel-breakout + momentum-band confirmation is not an edge on 1h crypto in this window.
