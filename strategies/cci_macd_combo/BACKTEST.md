# CCI + MACD Combo — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 35 | 37.1% | -471.19 | -0.87 | -10.4% | -13.46 | 0.70 |
| ETH | 26 | 38.5% | -213.08 | -0.48 | -5.1% | -8.20 | 0.79 |
| HYPE | 26 | 34.6% | -214.73 | -0.53 | -3.7% | -8.26 | 0.78 |
| **Combined** | **87** | **36.8%** | **-899.00** | **-1.05** | **-5.1%** | **-10.33** | **0.75** |

Fees: total $754.31.
Exits: BTC {'signal': 18, 'stop': 17}; ETH {'stop': 15, 'signal': 11}; HYPE {'stop': 13, 'signal': 13}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29101.00.

## Verdict: LOSER — -$899.00 on 87 trades, combined Sharpe -1.05, MaxDD -5.1%.

A small, consistent loser on all three coins (PF 0.70–0.79, win
rates 35–39%, expectancy -$8 to -$13 per trade). The system is
highly selective — only 87 trades in ~8 months — because the
entry needs two rare things to coincide: a CCI snap-back through
±100 and a MACD line already on the right side of its signal.
The MACD filter is the binding constraint: CCI snaps back early
in a recovery while the MACD line is still below its signal, so
most CCI extremes never become entries, and the ones that do are
late — the snap-back is already spent and the trade mean-reverts
into the 2xATR stop or back through the CCI 0 exit. The signal
exit does real work (42 of 87 exits), so the loss is in the entry
selectivity/timing, not a missing exit. No parameter was tuned;
the spec is shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Only 87 trades — a small sample, and every coin loses, so the
  direction is consistent even if the magnitude is noisy.
- The CCI ±100 snap-back + MACD-agreement combination is tuned
  for forex-style mean reversion; on 1h crypto the MACD leg lags
  the CCI leg by enough that the combined trigger is usually late.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
