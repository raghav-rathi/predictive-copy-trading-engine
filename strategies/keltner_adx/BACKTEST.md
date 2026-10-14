# Keltner Breakout (ADX-filtered) — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 2xATR stop, 2.5xATR chandelier trailing, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 104 | 25.0% | -$1,536 (-15.4%) | -1.57 | -19.3% | -$14.77 | 0.68 |
| ETH | 91 | 33.0% | -$628 (-6.3%) | -0.56 | -17.5% | -$6.91 | 0.84 |
| **Combined** | **195** | — | **-$2,164** | — | — | — | — |

## Verdict: LOSER

Same disease as the other 1h breakout systems (Donchian-20, Supertrend):
channel breaks on hourly crypto are mostly noise — 25-33% win rate with
the 2xATR stop absorbing the whipsaws. The ADX > 25 gate filters some chop
but the entries still arrive after the impulse. Consistent with the
Donchian calibration lesson: breakout edges on crypto need daily-scale
channels, not hourly ones. Not for capital as a standalone.
