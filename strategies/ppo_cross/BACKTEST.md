# PPO Signal Cross — Backtest

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
| BTC | 409 | 30.1% | -4,882 | -48.6% | -3.63 | -51.2% | -11.94 | 0.67 |
| ETH | 399 | 30.6% | -3,152 | -31.2% | -1.95 | -41.1% | -7.90 | 0.79 |
| HYPE | 413 | 32.7% | +282 | +2.8% | +0.30 | -17.1% | +0.68 | 1.02 |
| **Combined** | **1221** | — | **-7,752** | — | — | — | **-6.35** | — |

Total fees: $8,437.

## Verdict

LOSER — the worst in this batch. Combined −$7,752 across 1,221 trades (−$6.35 expectancy), with BTC down −48.6% of starting equity and a −51.2% max drawdown. The PPO normalisation is elegant but irrelevant here: dividing by price does not fix the signal cross's core defect, which is firing on every minor oscillator wiggle. Over 1,200 trades, the verdict is not ambiguous — this trigger loses on 1h crypto.
