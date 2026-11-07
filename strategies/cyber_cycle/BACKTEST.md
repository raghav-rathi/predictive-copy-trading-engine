# Cyber Cycle — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail. Window t in [1773525600000, 1794060000000]
(2026-03-14 22:00 UTC → 2026-11-07 13:00 UTC, last completed hour
bar; coordinator-verified on the fixed window, excluding the partial
14:00 UTC bar the standard runner pulls). $10k start per
coin, 1% risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee
+ 0.01% slippage per side, funding off.

**Bar counts used:** BTC 5704, ETH 5704, HYPE 5702.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 580 | 31.6% | -6418.23 | -5.06 | -66.0% | -11.07 | 0.62 |
| ETH | 582 | 31.8% | -4508.45 | -2.85 | -53.3% | -7.75 | 0.75 |
| HYPE | 559 | 35.8% | -963.84 | -0.32 | -32.6% | -1.72 | 0.96 |
| **Combined** | **1721** | **33.0%** | **-11890.52** | **-3.24** | **-46.3%** | **-6.91** | **0.79** |

Fees: total $10835.08.
Exits: {'signal': 879, 'stop': 842}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser, 1721 trades, -$11,890.52, PF 0.79 — the worst batch-29
strategy by dollars. The Signal-vs-its-own-delay cross fires on
nearly every cycle wiggle (580+ trades per coin in ~7.5 months), so
the strategy churns: 33.0% win rate, expectancy -$6.91/trade, and
$10,835.08 of fees alone nearly equal the total loss. BTC is the
worst leg (-$6,418.23, -66.0% MaxDD, Sharpe -5.06); HYPE is the
least bad (-$963.84, PF 0.96, near breakeven). The cycle filter
extracts oscillations, but on 1h crypto the "crosses" are dominated
by noise, not by tradeable cycle turns — no edge here as specified.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
