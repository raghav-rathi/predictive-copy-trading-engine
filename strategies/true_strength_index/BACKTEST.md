# True Strength Index — Backtest

Hyperliquid 1h candles, 2026-03-14 → 2026-10-18 (window
[1773446400000, 1792713599000)). Costs: 4.5 bps fee + 1 bp slippage
per side; no funding. 1% risk per trade, 3x max leverage, 1.5xATR stop,
2xATR trail, 120-bar max hold, 120-bar warmup.

| Coin | Bars | Trades | Win% | Net $ | Sharpe | Max DD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 5330 | 173 | 30.1% | -$2,593 | -2.01 | -27.7% | -$14.99 | 0.68 |
| ETH | 5330 | 177 | 26.6% | -$2,182 | -1.57 | -28.7% | -$12.33 | 0.74 |
| HYPE | 5328 | 157 | 26.8% | -$3,081 | -3.36 | -31.1% | -$19.62 | 0.53 |
| **Combined** | — | **507** | **~27.8%** | **-$7,855** | — | — | **-$15.49** | — |

## Honest verdict: loser

Red on every coin, 507 trades, every Sharpe deeply negative, win rate
~28% with profit factor 0.53–0.74. The double smoothing that makes TSI
elegant on daily equities makes it late on 1h crypto: by the time the
TSI/signal cross confirms in the right territory, the move is mostly
spent, and the opposite cross exits deep into the reversal. The
zero-territory filter did not save it — it only reduced trade count.
Verdict: **do not trade** as configured; a shorter smoothing pair or a
fundamentally faster entry trigger would be a different strategy, and
this one is filed as a verified negative result.
