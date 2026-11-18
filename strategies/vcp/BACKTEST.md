# Volatility Contraction Pattern (VCP) — Backtest

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
| BTC | 63 | 30.2% | -1415.54 | -2.24 | -18.2% | -22.47 | 0.50 |
| ETH | 59 | 30.5% | -1473.29 | -3.04 | -15.7% | -24.97 | 0.30 |
| HYPE | 58 | 36.2% | -168.89 | -0.25 | -7.7% | -2.91 | 0.90 |
| **Combined** | **180** | **32.2%** | **-3057.72** | **-2.82** | **-12.4%** | **-16.99** | **0.55** |

Fees: total $1392.30.
Exits: BTC {'signal': 34, 'stop': 29}; ETH {'signal': 37, 'stop': 22}; HYPE {'signal': 32, 'stop': 26}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,942.28.

## Verdict: LOSER — -$3,057.72 on 180 trades, combined Sharpe -2.82, MaxDD -12.4%.

VCP loses on 1h crypto: 180 trades, a 32.2% win rate, PF 0.55,
and -$3,057.72 net after $1,392.30 in fees. ETH is the worst
(-$1,473.29, PF 0.30, Sharpe -3.04), BTC nearly as bad
(-$1,415.54, PF 0.50); HYPE is near breakeven (-$168.89, PF
0.90) but does not save the combined result. The base validates
often (~29% of bars on BTC/ETH) and the breakout does trigger —
but the exit split (103 signal vs 77 stop) shows most breakouts
close back below the pivot within a few bars: the contraction
pattern forms, the breakout fails. The worst expectancy in the
batch (-$16.99/trade) comes from the losers running to the stop
while winners are cut by the failed-breakout exit. No parameter
was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 180 trades is a moderate sample; the loss is driven by BTC/ETH
  (HYPE near breakeven), so the verdict is coin-dependent but
  negative overall.
- The short side is a symmetric extension of a long-only pattern
  (see CALIBRATION.md); the long-only variant was not tested
  separately.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
