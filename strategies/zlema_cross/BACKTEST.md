# Zero-Lag EMA — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: de-lagged ZLEMA(10)/ZLEMA(30) cross,
opposite-cross exits, 2xATR stop, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 507 | 27.6% | −$6,283 | −62.8% | −4.71 | −65.1% | −$12.39 | 0.63 |
| ETH | 494 | 28.7% | −$4,540 | −45.7% | −2.70 | −55.9% | −$9.19 | 0.74 |
| HYPE | 469 | 38.2% | +$1,129 | +12.0% | +0.76 | −14.0% | +$2.41 | 1.06 |
| **Combined** | **1,470** | **31.4%** | **−$9,694** | — | — | — | **−$6.59** | — |

## Verdict: loser on majors — "zero lag" just means faster whipsaw

Removing the EMA's lag also removes its smoothing, and on 1h crypto
that trade is a bad one: 1,470 trades, Sharpe −4.71 on BTC. The fast
(5,15) variant is catastrophic (−$21,202, 3,016 trades). The slow
(20,60) variant flips the story (combined +$745, HYPE Sharpe 1.61) —
which says the de-lagging only works when the base periods are long
enough that the residual lag being removed was actually the problem.
As shipped, this is a loser; the slow variant is worth a walk-forward
look.
