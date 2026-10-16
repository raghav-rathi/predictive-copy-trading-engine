# inside_bar — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: inside bar + EMA50 bias, 2-bar breakout watch
on mother-bar extremes, 2xATR stop, 4xATR target (~2R), 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 181 | 33.7% | −$1,633 | −15.1% | −1.05 | −20.3% | −$9.02 | 0.86 |
| ETH | 187 | 37.4% | −$128 | −0.9% | +0.07 | −20.8% | −$0.68 | 0.99 |
| HYPE | 154 | 39.6% | +$953 | +10.1% | +0.83 | −12.0% | +$6.19 | 1.10 |
| **Combined** | **522** | **36.8%** | **−$808** | — | — | — | **−$1.55** | — |

## Verdict: HYPE-only winner, majors chop it up

The breakout watch works on HYPE (+10.1%, Sharpe 0.83, 1.10 profit
factor) and dies on BTC (−15.1%): hourly BTC spends most of 2026
chopping through the EMA50, so the bias filter arms setups into
mean-reversion instead of trend continuation. ETH is flat (−0.9%).
Combined −$808 — no cross-coin edge. The mother-bar-break trigger is
real on the one coin that trended (HYPE); elsewhere the 2R target gets
faded before it fills. Calibration (see CALIBRATION.md) shows a 3-bar
watch beats the published 2-bar watch on this data, but the shipped
config keeps the published 2-bar rule.
