# Sperandeo 2B Reversal — Backtest

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
| BTC | 13 | 30.8% | -591.94 | -1.74 | -7.6% | -45.53 | 0.24 |
| ETH | 11 | 27.3% | -101.49 | -0.24 | -3.8% | -9.23 | 0.79 |
| HYPE | 15 | 20.0% | -330.65 | -0.90 | -5.9% | -22.04 | 0.61 |
| **Combined** | **39** | **25.6%** | **-1024.08** | **-1.38** | **-4.6%** | **-26.26** | **0.51** |

Fees: total $307.85.
Exits: BTC {'stop': 12, 'signal': 1}; ETH {'stop': 10, 'signal': 1}; HYPE {'stop': 14, 'signal': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,975.92.

## Verdict: LOSER — -$1,024.08 on 39 trades, combined Sharpe -1.38, MaxDD -4.6%.

The 2B failed retest loses on 1h crypto: 39 trades, a 25.6% win
rate, PF 0.51, and -$1,024.08 net after $307.85 in fees. No coin
wins — BTC is the worst (PF 0.24, expectancy -$45.53/trade),
HYPE wins only 20.0% of its 15 trades, and ETH is the least bad
at -$101.49. The exit split (36 stop vs 3 signal) shows the
pattern's own exits almost never save a trade: entries fade a
fresh extreme, and on 1h bars the "failed" retest usually keeps
going into the 2xATR stop. The sample is small (39 trades), so
the magnitude is uncertain, but the direction is consistent
across all three coins. No parameter was tuned; the spec shipped
as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Only 39 trades — the loss is consistent across coins but the
  per-coin numbers are noisy; do not over-read the exact dollar
  figures.
- The retest deadline (28 bars) and failure window (20 bars) are
  interpretation choices (see CALIBRATION.md); a different
  deadline trades a different, overlapping set of patterns.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
