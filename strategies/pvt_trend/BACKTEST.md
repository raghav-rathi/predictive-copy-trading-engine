# Price-Volume Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: PVT/MA20 cross entries, opposite-cross exits,
2xATR stop, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 421 | 24.2% | −$3,443 | −32.0% | −1.55 | −47.9% | −$8.18 | 0.78 |
| ETH | 447 | 22.6% | −$4,638 | −43.7% | −2.34 | −57.0% | −$10.38 | 0.68 |
| HYPE | 374 | 31.8% | +$1,672 | +17.7% | +1.02 | −14.8% | +$4.47 | 1.10 |
| **Combined** | **1,242** | **25.9%** | **−$6,409** | — | — | — | **−$5.16** | — |

## Verdict: loser on majors, positive on HYPE (regime-dependent)

The familiar batch pattern: the pressure-cross system rides HYPE's 2026
trend phases (+17.7%, Sharpe 1.02) and bleeds on BTC/ETH chop. 1,242
trades at a 25.9% win rate means fee drag ($8.3k combined) does most of
the damage — the MA20 cross is too fast for 1h pressure noise. The
calibration sweep confirms slower is better (MA40 halves the loss and
lifts HYPE to Sharpe 1.90), but nothing here clears the bar for live
capital.
