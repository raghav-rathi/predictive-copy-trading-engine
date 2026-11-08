# Three White Soldiers — Backtest

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
| HYPE | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| **Combined** | **0** | **0.0%** | **0.00** | **0.00** | **0.0%** | **0.00** | **0.00** |

Fees: total $0.00.
Exits: none.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Zero trades on all three coins — untestable as specified.
The pattern never completes once in 15,667 bars. Verified genuine,
not a bug: the unit tests prove the pattern fires on crafted data,
and a diagnostic on real BTC data found 169 qualifying bullish
candles (153 bearish) but zero runs of three in a row — the
four-way conjunction (higher close + open inside prev body + wick
≤ 25% + body ≥ 0.5×ATR) three bars running is too strict for 1h
crypto. No PnL verdict is possible; the spec as written produces no
signal on this market/timeframe.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
