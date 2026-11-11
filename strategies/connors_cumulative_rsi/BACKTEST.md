# Connors Cumulative RSI — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794402000000) (2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5776, ETH 5776, HYPE 5774.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 26 | 69.2% | 425.63 | 1.19 | -3.7% | 16.37 | 1.64 |
| ETH | 40 | 47.5% | -398.33 | -0.82 | -8.2% | -9.96 | 0.72 |
| HYPE | 23 | 78.3% | 511.21 | 1.56 | -2.2% | 22.23 | 2.11 |
| **Combined** | **89** | **61.8%** | **538.51** | **0.84** | **-1.8%** | **6.05** | **1.21** |

Fees: total $689.18.
Exits: BTC {'signal': 20, 'stop': 6}; ETH {'signal': 25, 'stop': 15}; HYPE {'signal': 18, 'stop': 5}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30,538.51.

## Verdict: Marginal — nominally +$538.51 on 89 trades, not convincing evidence of edge.

The combined number is positive, but the per-coin split kills the
story: BTC +$426 and HYPE +$511 against ETH −$398, with ETH the
highest-trade coin (40) and the only one with a sub-1.0 profit factor
(0.72). A 61.8% win rate with a $6.05 expectancy and PF 1.21 is the
profile of small wins grinding against larger losses, and the signal
exits (63 of 89) show the cum_rsi-0 exit does most of the work — the
±100 entries themselves are rare, clustered events because the
never-reset sum drifts with history length and sits far outside ±100
for long stretches. One window, one asset class, no out-of-sample
check: this is a curiosity to watch, not a system to trade.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Entries cluster after long one-sided runs (history-length drift);
  the 89-trade sample is not independent evidence.
- The published Connors/Alvarez system is a different, bounded
  2-day variant (see CALIBRATION.md); this spec's unbounded sum was
  tested as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
