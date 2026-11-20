# Stochastic %K/%D Cross + MACD Histogram — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014. (HYPE's cache
starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 31 | 32.3% | -670.05 | -2.29 | -7.9% | -21.61 | 0.43 |
| ETH | 28 | 32.1% | -291.41 | -0.96 | -5.0% | -10.41 | 0.57 |
| HYPE | 38 | 36.8% | -296.58 | -0.74 | -4.0% | -7.80 | 0.77 |
| **Combined** | **97** | **34.0%** | **-1258.04** | **-2.01** | **-4.4%** | **-12.97** | **0.60** |

Fees: total $736.52.
Exits: BTC {'signal': 23, 'stop': 8}; ETH {'signal': 23, 'stop': 5}; HYPE {'signal': 27, 'stop': 11}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,741.96.

## Verdict: LOSER (small, consistent) — -$1,258.04 on 97 trades, combined Sharpe -2.01, MaxDD -4.4%.

The dual-confirmation gate makes this a rare-signal strategy
(97 trades in ~8 months across three coins) and the signals it
does take lose on every coin: win rate 32–37%, profit factor
0.43–0.77. The exit mix is signal-heavy (73 of 97 trades end on
a signal exit), so the strategy exits on its own terms — the
entries are just wrong more often than right, and the winners do
not pay for the losers. The loss is small in dollars because the
trade count is low, but the sign is consistent across all three
coins. No parameter was tuned; the spec shipped as written, and
the alternates in CALIBRATION.md lose too.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Only 97 trades — a small sample, but all three coins agree in
  sign and the per-coin losses are all in the same few-hundred
  dollar range.
- The %K<30 / %K>70 gate is evaluated on the cross bar only; a
  cross that happens one bar after %K leaves the extreme zone
  does not enter. See CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
