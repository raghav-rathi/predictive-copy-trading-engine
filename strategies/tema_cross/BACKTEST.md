# TEMA Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794402000000) (2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5776, ETH 5776, HYPE 5774.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 577 | 30.5% | -6149.93 | -4.47 | -63.7% | -10.66 | 0.64 |
| ETH | 583 | 32.6% | -3170.79 | -1.52 | -48.7% | -5.44 | 0.84 |
| HYPE | 571 | 33.5% | -1193.15 | -0.44 | -34.6% | -2.09 | 0.95 |
| **Combined** | **1731** | **32.2%** | **-10513.86** | **-2.58** | **-42.6%** | **-6.07** | **0.82** |

Fees: total $11261.24.
Exits: BTC {'signal': 291, 'stop': 286}; ETH {'signal': 293, 'stop': 290}; HYPE {'signal': 313, 'stop': 258}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$19,693.42.

## Verdict: LOSER — -$10,513.86 on 1,731 trades, the worst batch-33 result by dollars.

The unfiltered 9/21 TEMA cross is a whipsaw machine on 1h crypto: it
fired ~575 trades per coin in ~8 months (roughly 2–3 per day per coin),
lost on all three coins, and BTC's Sharpe of -4.47 with a -63.7% max
drawdown means the BTC leg alone gave back nearly two-thirds of its
$10k. Win rate ~32% with profit factor 0.64–0.95 is not a near-miss —
it is a systematically wrong-way signal at this speed. Fees alone were
$11,261.24, more than the net loss: even before fees the system barely
breaks even, so every cross is paying the spread to flip direction.
The mechanism is visible in the unit tests: TEMA tracks a linear move
with near-zero lag, so on a steady ramp the fast and slow TEMAs sit
almost on top of each other and flip on noise — the cross fires, then
fires back. Roughly half of all exits are the opposite cross (signal)
and half are the ATR stop, so neither the exit nor the stop rescues
it. This is exactly what the SMA200 filter in `tema_trend` exists to
prevent: the filter is the system, and removing it leaves noise.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,731-trade sample: the loss is statistically solid, not noise —
  the verdict is a genuine rejection, not inconclusive.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
