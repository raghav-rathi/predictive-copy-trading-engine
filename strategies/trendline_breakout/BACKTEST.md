# Trendline Breakout — Backtest

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
| BTC | 320 | 32.2% | -2802.06 | -1.79 | -37.4% | -8.76 | 0.78 |
| ETH | 342 | 31.9% | -3332.25 | -2.02 | -44.7% | -9.74 | 0.75 |
| HYPE | 297 | 34.3% | -1920.14 | -1.21 | -25.1% | -6.47 | 0.84 |
| **Combined** | **959** | **32.7%** | **-8054.46** | **-2.46** | **-33.7%** | **-8.40** | **0.79** |

Fees: total $6727.33.
Exits: BTC {'stop': 237, 'signal': 83}; ETH {'stop': 242, 'signal': 100}; HYPE {'stop': 230, 'signal': 67}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$21,945.54.

## Verdict: LOSER — -$8,054.46 on 959 trades, combined Sharpe -2.46, MaxDD -33.7%.

Demark-style trendline breaks lose on every coin on this window:
BTC -$2,802.06 (PF 0.78), ETH -$3,332.25 (PF 0.75, MaxDD -44.7%),
HYPE -$1,920.14 (PF 0.84). Win rates sit at 32–34% with expectancy
-$6.47 to -$9.74 per trade, and the system is the most active of
this batch (959 trades — a new line break fires constantly on 1h
bars, so the 2xATR stop is hit 709 times vs 250 signal exits).
The 5-bar pivot-confirmation lag means the line is drawn through
pivots that are already stale by the time it exists, and a
straight line through two noisy swing highs/lows on 1h crypto is
crossed and re-crossed by ordinary chop — the "break" carries no
momentum information. Do not trade as-is; the entry needs a
re-test/confirmation filter it does not have, and no parameter
was tuned to try to rescue it.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 959-trade sample, but the loss is broad-based across all three
  coins, so it is not a one-coin artifact.
- The exit split (709 stop / 250 signal) shows the system is
  mostly stop-driven: the opposite-line exit rarely gets the
  chance to pay off before the stop does.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
