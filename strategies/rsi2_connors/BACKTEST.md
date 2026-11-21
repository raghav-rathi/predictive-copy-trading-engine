# Connors RSI(2) — Backtest

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
| BTC | 148 | 56.1% | -2048.99 | -3.42 | -23.1% | -13.84 | 0.51 |
| ETH | 160 | 60.0% | -1645.03 | -2.36 | -17.4% | -10.28 | 0.63 |
| HYPE | 144 | 57.6% | -1028.11 | -1.75 | -11.6% | -7.14 | 0.71 |
| **Combined** | **452** | **58.0%** | **-4722.13** | **-3.73** | **-16.7%** | **-10.45** | **0.61** |

Fees: total $3155.09.
Exits: BTC {'signal': 112, 'stop': 36}; ETH {'signal': 124, 'stop': 36}; HYPE {'signal': 113, 'stop': 31}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$25,277.87.

## Verdict: LOSER — -$4,722.13 on 452 trades, combined Sharpe -3.73, MaxDD -16.7%.

The win rate looks healthy (58.0% combined) but the profit factor
is 0.61: average losses are far larger than average wins. Buying
every CRSI < 10 dip in a window dominated by a grinding downtrend
catches falling knives — the 50-cross exit gets out, but only
after the position has usually run well past the entry. Most exits
are signal exits (349 of 452), not stops, so the loss is in the
signal logic itself, not the risk layer. No parameter was tuned;
the spec shipped as written, and both calibration alternates lost
more money (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 452 trades is a solid sample and all three coins agree in sign —
  the loss is not a one-coin fluke.
- CRSI on 1h bars fires far more often than Connors' daily-bar
  design; the mean-reversion premise does not survive the
  timeframe transfer here.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
