# NVI/PVI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: NVI/EMA255 cross with PVI agreement filter,
NVI cross-back exits, 2xATR stop, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 79 | 32.9% | −$1,616 | −16.2% | −2.35 | −17.6% | −$20.46 | 0.52 |
| ETH | 85 | 30.6% | −$1,240 | −12.4% | −1.47 | −15.4% | −$14.59 | 0.65 |
| HYPE | 94 | 26.6% | +$141 | +1.4% | +0.22 | −16.3% | +$1.50 | 1.04 |
| **Combined** | **258** | **29.8%** | **−$2,715** | — | — | — | **−$10.52** | — |

## Verdict: loser (sparse but negative-expectancy)

Fosback's regime read doesn't survive the port: 255 1h bars is ~10.6
days, not a year, so the "smart money regime" being timed is a
fortnight-long wobble. The PVI-agreement filter keeps trade count low
(258), but expectancy is deeply negative (−$10.52/trade) — when the
regime call is wrong, the 2xATR stop and 120-bar hold let it bleed.
HYPE is flat (+$141), not a win. The EMA500 variant loses less, which
says the only fix is "be even slower," i.e. there is no 1h edge here.
