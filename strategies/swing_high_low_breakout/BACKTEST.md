# Swing High Low Breakout — Backtest

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
| BTC | 289 | 31.1% | -4262.29 | -2.85 | -44.0% | -14.75 | 0.68 |
| ETH | 284 | 28.2% | -4810.00 | -3.82 | -49.4% | -16.94 | 0.57 |
| HYPE | 252 | 33.7% | -1658.75 | -1.07 | -21.1% | -6.58 | 0.86 |
| **Combined** | **825** | **30.9%** | **-10731.04** | **-3.50** | **-36.7%** | **-13.01** | **0.70** |

Fees: total $5614.48.
Exits: BTC {'stop': 238, 'signal': 51}; ETH {'stop': 232, 'signal': 52}; HYPE {'stop': 197, 'signal': 55}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$19,207.60.

## Verdict: LOSER — -$10,731.04 on 825 trades, combined Sharpe -3.50, MaxDD -36.7%. Worst batch-38 strategy by dollars.

Swing-structure breakouts are the worst performer of the batch:
ETH -$4,810.00 (PF 0.57, Sharpe -3.82, MaxDD -49.4% — the
account halves), BTC -$4,262.29 (PF 0.68, MaxDD -44.0%), HYPE
-$1,658.75 (PF 0.86). Win rates of 28–34% with expectancy
-$6.58 to -$16.94 per trade say the entries are systematically
wrong-way: on 1h crypto, a close through the last 5-bar swing
high with ascending swing lows is more often the last push
before a reversal than the start of a leg. The ascending-lows
/ descending-highs filter does not filter anything in
practice — it is true most of the time in any trending stretch,
so it adds almost no selectivity over a raw swing break. The
exit split (158 signal exits vs 667 stops) shows the
opposite-structure exit rarely saves a trade; most positions
die on the 2xATR stop or the trail first. Combined Sharpe -3.50
is the worst of the batch by a wide margin.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 825-trade sample, and the loss is broad-based (all three coins
  negative, PF 0.57–0.86) — the edge is absent, not one-coin driven.
- The opposite-structure exit fires on only 158/825 trades; the
  reported result is mostly the entry + harness stop/trail.
- The 2-bar pivot confirmation lag means entries fire at least
  2 bars after the pivot bar; a faster (lookahead) pivot would
  not be tradeable and was correctly not used.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
