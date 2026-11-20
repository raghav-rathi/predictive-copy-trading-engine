# Adaptive MACD — Backtest

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
| BTC | 321 | 31.8% | -3484.60 | -2.15 | -36.9% | -10.86 | 0.74 |
| ETH | 339 | 31.9% | -2434.49 | -1.31 | -30.1% | -7.18 | 0.84 |
| HYPE | 338 | 34.9% | 331.44 | 0.38 | -16.9% | 0.98 | 1.02 |
| **Combined** | **998** | **32.9%** | **-5587.65** | **-1.31** | **-22.3%** | **-5.60** | **0.87** |

Fees: total $7210.22.
Exits: BTC {'stop': 239, 'signal': 82}; ETH {'stop': 257, 'signal': 82}; HYPE {'stop': 247, 'signal': 91}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,635.10.

## Verdict: LOSER — -$5,587.65 on 998 trades, combined Sharpe -1.31, MaxDD -22.3%.

BTC and ETH both lose with PF 0.74 / 0.84 and Sharpe -2.15 / -1.31;
only HYPE is nominally green (+$331.44, PF 1.02) and it does not
offset the other two. The adaptive smoothing does not save the
classic MACD-cross problem on 1h crypto: crosses fire into chop,
~75% of trades end on the harness stop, and fees ($7,210.22)
exceed the gross loss. No parameter was tuned; the spec shipped as
written, and both calibration alternates also lose (see
CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 998 trades is a large sample and all three coins agree the
  strategy loses on BTC/ETH — the loss is not a one-coin artifact.
- The ER-10 / period-range choices are the spec's KAMA-style
  reading; other adaptive-MACD constructions exist.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
