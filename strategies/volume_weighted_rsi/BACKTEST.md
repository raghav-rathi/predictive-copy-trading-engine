# Volume-Weighted RSI — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014. (The CSVs each
contain one further bar at exactly END_MS; the half-open window
excludes it. HYPE's cache starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 166 | 38.6% | -2145.48 | -1.93 | -28.3% | -12.92 | 0.74 |
| ETH | 170 | 43.5% | -1178.31 | -0.88 | -22.1% | -6.93 | 0.86 |
| HYPE | 174 | 37.9% | -738.82 | -0.55 | -14.0% | -4.25 | 0.91 |
| **Combined** | **510** | **40.0%** | **-4062.61** | **-1.67** | **-20.0%** | **-7.97** | **0.84** |

Fees: total $4107.67.
Exits: BTC {'stop': 113, 'signal': 53}; ETH {'stop': 106, 'signal': 64}; HYPE {'stop': 116, 'signal': 58}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$25,976.91 — $39.52 above $30,000 + net PnL (-$4,062.61), which is the
mark-to-market of positions still open at the window end (net PnL
counts closed trades only).

## Verdict: LOSER — -$4,062.61 on 510 trades, combined Sharpe -1.67, MaxDD -20.0%.

All three coins lose with profit factors 0.74–0.91, and the exit mix
tells the story: 335 of 510 trades end on the harness stop/trail
vs 175 on the RSI-50 signal exit. The volume-weighted RSI crosses
30/70 often enough to trade, but the mean-reversion entries keep
running into the 2xATR stop before the RSI can cross back through
50 — the signal exit is not doing the work, the stop is. Total fees
$4,107.67 roughly equal the entire net loss, so even gross of costs
the strategy is ~breakeven-to-negative, not a fee-drag story alone.
No parameter was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 510 trades is a decent sample, and all three coins agree in sign —
  this is a consistent loser, not a one-coin fluke.
- The first-valid-RSI cross artifact (see CALIBRATION.md) is
  suppressed by WARMUP=40 and never trades.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
