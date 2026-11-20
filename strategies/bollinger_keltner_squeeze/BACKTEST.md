# Bollinger/Keltner Squeeze — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 131 | 34.4% | -345.08 | -0.20 | -14.3% | -2.63 | 0.95 |
| ETH | 136 | 39.0% | 739.64 | 0.63 | -12.9% | 5.44 | 1.12 |
| HYPE | 112 | 32.1% | -28.51 | 0.06 | -11.5% | -0.25 | 0.99 |
| **Combined** | **379** | **35.4%** | **366.04** | **0.20** | **-9.3%** | **0.97** | **1.02** |

Fees: total $3405.32.
Exits: BTC {'stop': 126, 'signal': 5}; ETH {'stop': 126, 'signal': 10}; HYPE {'stop': 108, 'signal': 4}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30,366.04.

## Verdict: WINNER (nominal, thin) — +$366.04 on 379 trades, combined Sharpe 0.20, MaxDD -9.3%.

Do not read an edge into this: the combined profit is +$366 on
$3,405 of fees with PF 1.02 — statistically indistinguishable from
luck. ETH is the only green coin (+$739.64, PF 1.12); BTC (-$345.08)
and HYPE (-$28.51) are flat-to-negative. Almost every trade ends on
the harness stop/trail (360 of 379 exits are 'stop'), not on the
opposite squeeze signal (19) — the squeeze-fire entry has no
follow-through exit of its own in this window, so trades live or die
on the 2xATR stop. No parameter was tuned; the spec shipped as
written, and both calibration alternates lost money (see
CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 379 trades is a moderate sample, but the three coins disagree in
  sign and the combined PF is 1.02 — not a robust edge claim.
- The Keltner mid uses EMA(20) (standard Carter/TTM construction)
  while the Bollinger mid uses SMA(20); see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
