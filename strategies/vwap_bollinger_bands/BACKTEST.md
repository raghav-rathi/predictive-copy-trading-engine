# VWAP Bollinger Bands — Backtest

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
| BTC | 343 | 50.7% | -4008.81 | -4.64 | -41.9% | -11.69 | 0.53 |
| ETH | 349 | 52.1% | -3653.12 | -3.25 | -39.1% | -10.47 | 0.63 |
| HYPE | 386 | 53.9% | -4050.19 | -4.50 | -43.0% | -10.49 | 0.62 |
| **Combined** | **1078** | **52.3%** | **-11712.13** | **-5.81** | **-40.3%** | **-10.86** | **0.60** |

Fees: total $7588.73.
Exits: BTC {'signal': 252, 'stop': 91}; ETH {'signal': 247, 'stop': 102}; HYPE {'signal': 262, 'stop': 124}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$18,287.87, exactly $30,000 + net PnL — no position was open at the
window end.

## Verdict: LOSER (worst of batch 41) — -$11,712.13 on 1,078 trades, combined Sharpe -5.81, MaxDD -40.3%.

The win rate looks respectable (52.3% combined, every coin above
50%) and most trades exit on the signal (761 of 1,078 exit at VWAP),
yet the profit factor is 0.60 — the wins are small and the losses
are big. That is the signature of fading a 2-SD band on 1h crypto:
the exit at VWAP books a small reversion, but when price keeps
trending the trade rides to the stop or trails out at a large
loss, and the ADX < 25 filter does not keep those trades out.
The strategy also overtrades (1,078 trades, the most of the three
batch-41 strategies), so fees of $7,588.73 compound the damage —
but fees are only ~65% of the net loss; gross of costs it still
loses ~$4,100. No parameter was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,078 trades is a large sample, and all three coins agree in sign
  with MaxDD -39% to -43% each — this is a consistent loser, not a
  one-coin fluke.
- 24/7 crypto has no true session open: the UTC-day anchor resets
  the bands at midnight, and early-day bands are computed from very
  few bars (see CALIBRATION.md). The backtest includes that noise
  as shipped.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
