# EMA Ribbon — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000) (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 147 | 25.2% | -2143.33 | -1.97 | -24.9% | -14.58 | 0.64 |
| ETH | 151 | 30.5% | -879.43 | -0.67 | -14.4% | -5.82 | 0.86 |
| HYPE | 154 | 35.7% | 1244.62 | 1.04 | -9.2% | 8.08 | 1.19 |
| **Combined** | **452** | **30.5%** | **-1778.14** | **-0.63** | **-10.8%** | **-3.93** | **0.91** |

Fees: total $3347.99.
Exits: {'stop': 320, 'signal': 132}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 452 trades, −$1778.14, PF 0.91. Only HYPE
is green (+$1244.62, Sharpe 1.04); BTC is firmly red (−$2143.33,
Sharpe −1.97, MaxDD −24.9%) and ETH mildly red (−$879.43). Win rate is
low everywhere (25–36%): entering on the first-alignment bar means
buying after the move has already run, and the exit mix is
stop-heavy (320 of 452 exits hit the ATR stop/trail), so positions
rarely survive to the alignment-break/EMA34 exit. A coin-dependent
result, not a universal ribbon edge.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
