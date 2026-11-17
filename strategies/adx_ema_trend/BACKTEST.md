# ADX EMA Trend — Backtest

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
| BTC | 21 | 28.6% | -530.98 | -1.22 | -6.6% | -25.28 | 0.33 |
| ETH | 32 | 40.6% | -369.50 | -0.65 | -7.2% | -11.55 | 0.70 |
| HYPE | 23 | 43.5% | 327.91 | 0.68 | -5.7% | 14.26 | 1.29 |
| **Combined** | **76** | **38.2%** | **-572.58** | **-0.57** | **-3.4%** | **-7.53** | **0.82** |

Fees: total $597.66.
Exits: BTC {'stop': 20, 'signal': 1}; ETH {'stop': 27, 'signal': 5}; HYPE {'stop': 22, 'signal': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,427.42.

## Verdict: LOSER — -$572.58 on 76 trades, combined Sharpe -0.57, MaxDD -3.4%.

The ADX filter is too strict for 1h crypto: only 76 trades in ~8
months across three coins, and the filter did not buy edge — BTC
(-$530.98, PF 0.33, win rate 28.6%) and ETH (-$369.50, PF 0.70)
both lose, and only HYPE wins (+$327.91, PF 1.29) on a 23-trade
sample. The exit split is the story: 69 of 76 trades ended on the
harness stop/trail and only 7 on a signal exit, so the ADX < 20 /
reverse-cross exit almost never gets a chance — entries are rare
and, once in, the trade is usually stopped out before the trend
signal turns. The ADX-at-the-cross requirement also misses trends
that start from flat, because ADX is still seeding when the first
cross fires (see CALIBRATION.md). No parameter was tuned; the
spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 76-trade sample — thin; the HYPE "win" is 23 trades and is not
  evidence of a real edge.
- The signal exit fired on only 7/76 trades; the reported result
  is really the entry + harness stop/trail, not the full
  cross-to-cross system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
