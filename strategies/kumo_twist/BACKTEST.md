# Ichimoku Kumo Twist — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 166 | 35.5% | -1129.46 | -0.84 | -18.6% | -6.80 | 0.84 |
| ETH | 167 | 34.7% | -425.48 | -0.22 | -16.9% | -2.55 | 0.94 |
| HYPE | 147 | 37.4% | 174.33 | 0.23 | -11.5% | 1.19 | 1.03 |
| **Combined** | **480** | **35.8%** | **-1380.60** | **-0.45** | **-12.8%** | **-2.88** | **0.94** |

Fees: total $4217.74.
Exits: {'stop': 412, 'signal': 68}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined (−$1,380.60, PF 0.94, Sharpe −0.45) — the mildest loser of the batch, but still a loser.

The causal (unshifted) twist is a slow signal — only 480 trades —
and it loses a little on BTC and ETH while HYPE squeaks out +$174.33
(PF 1.03, 147 trades; nominal, not a real edge). 412 of 480 exits
(86%) hit the ATR stop/trail rather than the opposite twist: twists
are rare and the stop usually fires first, so the strategy is mostly
riding the risk layer, not the cloud. The textbook twist is a
slow-moving regime hint, not a timing trigger, and on 1h crypto the
unshifted version behaves the same way. Not tradeable as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The unshifted-span construction is a deliberate departure from
  textbook Ichimoku (see README/CALIBRATION): results say nothing
  about the displaced-cloud twist.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
