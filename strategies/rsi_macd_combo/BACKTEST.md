# RSI + MACD Confluence — Backtest

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
| BTC | 351 | 21.1% | -4,030 | -40.4% | -3.75 | -43.0% | -11.48 | 0.63 |
| ETH | 372 | 19.4% | -2,966 | -29.8% | -2.41 | -34.2% | -7.97 | 0.75 |
| HYPE | 316 | 27.2% | +1,056 | +10.6% | +0.81 | -10.6% | +3.34 | 1.11 |
| **Combined** | **1039** | — | **-5,940** | — | — | — | **-5.72** | — |

Total fees: $7,812.

## Verdict

LOSER. Combined −$5,940 across 1,039 trades (−$5.72 expectancy). The confluence idea is sound in principle — requiring two indicators to agree should cut false signals — but on this window it mostly delays entries into moves already underway while the RSI-recross exit churns positions: 19.4% win rate on ETH is the batch's lowest single-leg print. HYPE's green leg (+$1,056) is the only bright spot and is far too thin to outweigh two heavy losing legs.
