# Morning/Evening Star — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1794060000000] (2026-03-14 22:00 UTC →
2026-11-07 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5704, ETH 5704, HYPE 5702.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 39 | 30.8% | -790.96 | -1.27 | -14.6% | -20.28 | 0.62 |
| ETH | 53 | 41.5% | -38.42 | 0.00 | -7.9% | -0.72 | 0.99 |
| HYPE | 56 | 37.5% | 132.01 | 0.24 | -7.2% | 2.36 | 1.05 |
| **Combined** | **148** | **37.2%** | **-697.37** | **-0.49** | **-5.6%** | **-4.71** | **0.91** |

Fees: total $1127.43.
Exits: {'stop': 137, 'signal': 11}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 148 trades, -$697.37, PF 0.91 — the star
pattern does not pay on 1h crypto: BTC is the worst leg (-$790.96,
expectancy -$20.28/trade), ETH is flat (-$38.42), only HYPE is
marginally green (+$132.01). The exit mix is damning for the pattern
itself: only 11 of 148 positions exited on the opposite star, while
137 hit the ATR stop/trail — entries rarely see a follow-through
reversal strong enough to reach the opposite-pattern exit, and the
2xATR stop does most of the closing. Classic textbook pattern,
no edge at this timeframe.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
