# Donchian Channel Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795269600000) (2026-03-14 22:00 UTC →
2026-11-21 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6040, ETH 6040, HYPE 6038.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 222 | 33.3% | -1598.67 | -0.91 | -24.0% | -7.20 | 0.84 |
| ETH | 211 | 34.6% | 382.08 | 0.34 | -17.9% | 1.81 | 1.04 |
| HYPE | 234 | 33.8% | -881.17 | -0.43 | -22.0% | -3.77 | 0.92 |
| **Combined** | **667** | **33.9%** | **-2097.76** | **-0.48** | **-14.3%** | **-3.15** | **0.93** |

Fees: total $5062.32.
Exits: BTC {'stop': 199, 'signal': 23}; ETH {'stop': 189, 'signal': 22}; HYPE {'stop': 207, 'signal': 27}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,902.24.

## Verdict: LOSER — -$2,097.76 on 667 trades, combined Sharpe -0.48, MaxDD -14.3%.

Only ETH is green (+$382.08, PF 1.04) and only barely; BTC (-$1,598.67)
and HYPE (-$881.17) are both red. 595 of 667 exits are the harness
stop/trail, not the Donchian/Turtle signal exit (72) — the 20-bar
breakout entries do not follow through to the 10-bar exit before the
2xATR stop takes the trade out. The win rate (~34%) is too low for
the average win to cover the average loss at PF 0.93. No parameter
was tuned; the spec shipped as written, and both calibration
alternates lost more money (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 667 trades is a solid sample, but all three coins agree in
  direction only for ETH's thin green — no robust edge claim.
- The classic Turtle System 1 skip rule (skip a breakout if the
  previous breakout was a winner) was NOT implemented; see
  CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
