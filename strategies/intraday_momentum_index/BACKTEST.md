# Intraday Momentum Index — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 269 | 40.5% | -2336.05 | -1.64 | -30.9% | -8.68 | 0.82 |
| ETH | 275 | 42.9% | -926.73 | -0.49 | -29.1% | -3.37 | 0.92 |
| HYPE | 257 | 40.1% | -2358.57 | -1.82 | -25.2% | -9.18 | 0.79 |
| **Combined** | **801** | **41.2%** | **-5621.35** | **-1.82** | **-25.1%** | **-7.02** | **0.84** |

Fees: total $5858.29.
Exits: BTC {'stop': 181, 'signal': 88}; ETH {'stop': 185, 'signal': 90}; HYPE {'stop': 178, 'signal': 79}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,378.65.

## Verdict: Loser on paper (−$5,621.35, PF 0.84, Sharpe −1.82).

The IMI mean-reversion read loses on every coin in this window. It fires 801 trades in ~8 months, and two-thirds of them (544 of 801) die on the ATR stop — the 30/70 crossings mark short-lived intraday extremes that keep extending against the position on 1h crypto, so entries buy into falling knives and short into squeezes. Win rate 41.2% with PF 0.84 is a losing system before fees; after $5,858.29 of fees it is clearly negative, with a −25.1% combined drawdown. ETH is the least bad (−$926.73, PF 0.92) but still negative. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
