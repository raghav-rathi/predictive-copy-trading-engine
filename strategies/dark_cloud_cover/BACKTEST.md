# Dark Cloud Cover — Backtest

**Data:** Hyperliquid 1h candles from the local cache only
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000) (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| ETH | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| HYPE | 1 | 100.0% | 415.74 | 2.17 | -1.1% | 415.74 | inf |
| **Combined** | **1** | **100.0%** | **415.74** | **2.15** | **-0.4%** | **415.74** | **inf** |

Fees: total $5.47.
Exits: HYPE {'stop': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: One trade total — effectively untestable as specified.
A single HYPE piercing-pattern long won +$415.74 (exited on the ATR
stop), but one trade is not a track record and the 100% win rate /
infinite profit factor are meaningless at n=1. Verified genuine,
not a bug: the unit tests prove the pattern fires on crafted data,
and a diagnostic on real BTC data found the gap condition is the
binding constraint — bar 2 opening above bar 1's high happened only
twice in 5,223 bars, because 24/7 crypto has no session gaps. The
gap-based pattern as written essentially never triggers on 1h
crypto.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
