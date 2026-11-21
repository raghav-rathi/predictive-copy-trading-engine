# Chande Momentum Oscillator — Backtest

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
| BTC | 197 | 31.5% | -2195.61 | -1.38 | -23.8% | -11.15 | 0.79 |
| ETH | 200 | 37.5% | -764.08 | -0.38 | -18.7% | -3.82 | 0.92 |
| HYPE | 190 | 33.2% | -2793.60 | -2.36 | -31.9% | -14.70 | 0.68 |
| **Combined** | **587** | **34.1%** | **-5753.29** | **-1.89** | **-20.6%** | **-9.80** | **0.80** |

Fees: total $4307.90.
Exits: BTC {'stop': 164, 'signal': 33}; ETH {'stop': 160, 'signal': 40}; HYPE {'stop': 151, 'signal': 39}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,503.24.

## Verdict: LOSER — -$5,753.29 on 587 trades, combined Sharpe -1.89, MaxDD -20.6%.

All three coins lose, with win rates of only 31–38% and profit
factors 0.68–0.92. The CMO ±50 cross is a mean-reversion trigger
(crossing back out of an extreme), and on 1h crypto in this window
the extremes keep extending: entries buy/sell into momentum that
continues against the position, and 475 of 587 exits are the harness
stop/trail rather than the opposite cross (112 signal exits). No
parameter was tuned; the spec shipped as written, and both
calibration alternates also lost money (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The ±50 cross fires only after the oscillator has already been
  pinned at an extreme for a while, so entries are late by
  construction on trending moves.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
