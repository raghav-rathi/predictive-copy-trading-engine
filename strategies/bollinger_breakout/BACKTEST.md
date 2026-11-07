# Bollinger Band Squeeze Breakout — Backtest

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
| BTC | 192 | 25.0% | -1817.15 | -2.11 | -20.5% | -9.46 | 0.62 |
| ETH | 165 | 28.5% | -48.37 | 0.03 | -10.5% | -0.29 | 0.99 |
| HYPE | 210 | 31.4% | -955.98 | -1.10 | -13.0% | -4.55 | 0.80 |
| **Combined** | **567** | **28.4%** | **-2821.50** | **-1.32** | **-13.3%** | **-4.98** | **0.79** |

Fees: total $4799.53.
Exits: {'signal': 493, 'stop': 74}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 567 trades, -$2,821.50, PF 0.79 — the
squeeze breakout fails on 1h crypto in this window: breakouts after a
squeeze mostly snap back inside the bands, and the spec exit (close
back inside) cuts 87% of trades at a small loss while the 2xATR stop
rarely gets a chance to save a runner. No coin is green; ETH (-$48.37)
is closest to breakeven, BTC (-$1,817.15) worst. Win rate 28.4% with
expectancy -$4.98/trade — no edge here, reported as-is.

## Limitations

- Single ~7.7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
