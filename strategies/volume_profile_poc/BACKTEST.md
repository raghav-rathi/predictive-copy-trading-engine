# Volume Profile POC — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000] (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 329 | 25.8% | -5203.33 | -5.96 | -52.5% | -15.82 | 0.48 |
| ETH | 339 | 27.1% | -5034.18 | -5.73 | -52.4% | -14.85 | 0.53 |
| HYPE | 314 | 30.6% | -3825.65 | -4.17 | -40.4% | -12.18 | 0.57 |
| **Combined** | **982** | **27.8%** | **-14063.16** | **-9.20** | **-46.8%** | **-14.32** | **0.53** |

Fees: total $6149.30.
Exits: {'signal': 693, 'stop': 289}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser, 982 trades, -$14063.16, PF 0.53 — heavily red
on all three coins (BTC -$5203.33, ETH -$5034.18, HYPE -$3825.65).
The dip condition (low within 0.5×ATR of POC) is nearly always true
when price is near POC, so the strategy fires on almost every
close back across POC — ~1 trade per 16 bars — and the 26-31% win
rate cannot carry 2xATR stops. POC is not a reliable support /
resistance level on this 1h crypto window as specified; do not trade.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
