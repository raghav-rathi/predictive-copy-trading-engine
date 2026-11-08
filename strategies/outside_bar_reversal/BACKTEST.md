# Outside-Bar Reversal — Backtest

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
| BTC | 100 | 32.0% | -1573.77 | -2.08 | -22.9% | -15.74 | 0.62 |
| ETH | 88 | 31.8% | -953.69 | -1.19 | -15.9% | -10.84 | 0.75 |
| HYPE | 98 | 37.8% | 871.53 | 1.07 | -8.2% | 8.89 | 1.21 |
| **Combined** | **286** | **33.9%** | **-1655.93** | **-1.02** | **-8.8%** | **-5.79** | **0.86** |

Fees: total $2304.48.
Exits: BTC {'stop': 58, 'signal': 42}; ETH {'stop': 49, 'signal': 39}; HYPE {'stop': 49, 'signal': 49}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 286 trades, -$1655.93, PF 0.86 — BTC
(-$1573.77, Sharpe -2.08, MaxDD -22.9%) and ETH (-$953.69) are both
red; only HYPE (+$871.53, Sharpe 1.07, PF 1.21) is green. The exit
mix is near-even (156 stop exits vs 130 signal exits), so the signal
exits fire often but the reversals do not follow through on BTC/ETH.
No edge outside HYPE — treat as coin-dependent, not a universal
outside-bar edge.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
