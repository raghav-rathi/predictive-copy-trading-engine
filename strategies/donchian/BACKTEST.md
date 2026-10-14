# Donchian Breakout — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Calibration journey (the important part)

| Channel (entry/exit, 1h bars) | BTC | ETH |
|---|---|---|
| 20 / 10 | -15.3%, Sharpe -1.14, 139 trades | -14.8%, Sharpe -1.12, 131 trades |
| 120 / 60 | -9.9%, Sharpe -1.20, 53 trades | -0.5%, Sharpe +0.02, 44 trades |
| **480 / 240 (= 20/10 trading days)** | **+4.4%, Sharpe +0.74, 23 trades** | -5.7%, Sharpe -0.92, 23 trades |

The naive 20-bar port lost on both coins with 84% of exits via stop-loss:
it was trading noise, not breakouts. The Turtle edge only appears at the
system's native daily timeframe. Shipped default: 480/240.

## Shipped config results

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 23 | 34.8% | +$438 (+4.4%) | 0.74 | -5.4% | +$19.06 | 1.36 |
| ETH | 23 | 26.1% | -$569 (-5.7%) | -0.92 | -6.2% | -$24.72 | 0.66 |
| **Combined** | **46** | **30.4%** | **-$130 (-0.7%)** | — | — | -$2.83 | — |

## Verdict: MIXED / not a standalone edge

BTC at the true daily scale is modestly positive with a shallow drawdown,
but ETH fails outright and the combined book is negative. Classic Turtle
profile (low win rate, fat tails) needs more markets and longer samples to
judge; on this 7-month crypto window it does not clear the bar as a
single-strategy book. Candidate for a multi-strategy ensemble sleeve, not
for capital on its own.

## External validation

Independent walk-forward study (Wataru Suda, dev.to, Sep 2026) of a
20/10 Donchian + SMA50 filter + 2xATR stop on daily crypto bars,
2018–2026: stitched out-of-sample Sharpe **0.85** (in-sample 1.11),
beating re-optimized params in 4 of 6 OOS years. Converges with our
calibration finding: the Donchian edge lives at the daily scale with a
trend filter, not on intraday bars.
https://dev.to/wataru_suda_d295dab9cca4f/your-backtest-is-lying-to-you-walk-forward-analysis-and-the-deflated-sharpe-ratio-in-plain-python-36d7

## Limitations

- Single 7-month window, choppy-to-bearish crypto regime; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs the idealized stop-entry-on-breakout.
- ADX(14) > 20 gate is a modern addition, not in the original rules.
