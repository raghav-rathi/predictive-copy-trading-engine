# ATR Expansion Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 54 | 33.3% | -855.44 | -2.26 | -9.9% | -15.84 | 0.50 |
| ETH | 60 | 26.7% | -168.36 | -0.19 | -8.7% | -2.81 | 0.90 |
| HYPE | 41 | 29.3% | -154.98 | -0.46 | -3.5% | -3.78 | 0.79 |
| **Combined** | **155** | **29.7%** | **-1178.79** | **-1.13** | **-6.3%** | **-7.61** | **0.72** |

Fees: total $1283.82.
Exits: BTC {'signal': 42, 'stop': 12}; ETH {'signal': 48, 'stop': 12}; HYPE {'signal': 38, 'stop': 3}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,821.21.

## Verdict: LOSER — -$1,178.79 on 155 trades, combined Sharpe -1.13, MaxDD -6.3%.

The ATR expansion breakout loses on 1h crypto: 155 trades, a 29.7%
win rate, PF 0.72, and -$1,178.79 net after $1,283.82 in fees. No
coin wins — BTC is the worst (-$855.44, PF 0.50, expectancy -$15.84
per trade), ETH is near breakeven (-$168.36, PF 0.90) and HYPE is
near breakeven (-$154.98, PF 0.79). The tight-range + ATR-expansion
gates are very selective (only 155 trades in ~8 months across three
coins), but the breaks that do fire mostly fail: the exit split
(128 signal vs 27 stop) shows most trades end on the back-inside /
regime-faded signal exit rather than the stop, i.e. the expansion
fades or price falls back inside the range almost immediately.
No parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Only 155 trades, so the per-coin numbers are noisy — but the loss
  is present on all three coins and the PF is below 1 everywhere.
- The range uses closes, not highs/lows (see CALIBRATION.md); a
  high/low range would be wider and break even less often.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
