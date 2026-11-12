# Swing Failure Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 433 | 38.8% | -3642.59 | -2.21 | -49.4% | -8.41 | 0.80 |
| ETH | 419 | 39.6% | -4337.82 | -2.79 | -51.7% | -10.35 | 0.75 |
| HYPE | 453 | 38.9% | -3313.81 | -2.02 | -44.1% | -7.32 | 0.80 |
| **Combined** | **1305** | **39.1%** | **-11294.22** | **-3.33** | **-45.2%** | **-8.65** | **0.78** |

Fees: total $8338.49.
Exits: BTC {'stop': 296, 'signal': 137}; ETH {'stop': 282, 'signal': 137}; HYPE {'stop': 298, 'signal': 155}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$18,641.06.

## Verdict: LOSER — -$11,294.22 on 1,305 trades, combined Sharpe -3.33, MaxDD -45.2%.

The swing-failure pattern loses on every coin in this window, with
remarkably uniform numbers (win rate 38.8–39.6%, PF 0.75–0.80 on all
three) — the failure is systematic, not coin-specific. The mechanism's
flaw on 1h crypto: a 20-bar swing level on hourly bars is breached
constantly, so the pattern fires 1,305 times in ~5,823 bars and most
"failures" are just ordinary hourly noise — price pokes above a
20-bar high and closes back inside as a matter of routine, with no
trapped-breakout-trader reversal following. 876 of 1,305 trades end
on the harness stop/trail, and the $8,338.49 fee bill on 1,305 trades
is itself most of the loss. The pattern as taught assumes swing levels
that matter (daily/weekly structure, levels with real resting
liquidity); a rolling 20-bar high on 1h crypto carries none of that
weight. Do not trade this as specified.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,305-trade sample: large enough that the loss is not a small-sample
  fluke — the system is structurally wrong for 1h crypto as specified.
- The result is the 20-bar / 3-bar pattern + harness stop/trail as
  specified; using structurally significant swing levels (daily pivots,
  prior day high/low) would be a different system, not a tuning of
  this one.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
