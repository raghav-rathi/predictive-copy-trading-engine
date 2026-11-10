# Volume Zone Oscillator — Backtest

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
| BTC | 336 | 17.9% | -4822.09 | -4.96 | -48.9% | -14.35 | 0.47 |
| ETH | 282 | 23.8% | -2123.07 | -1.66 | -28.1% | -7.53 | 0.72 |
| HYPE | 301 | 24.6% | -2621.37 | -2.25 | -33.6% | -8.71 | 0.72 |
| **Combined** | **919** | **21.9%** | **-9566.52** | **-4.12** | **-34.2%** | **-10.41** | **0.63** |

Fees: total $5852.30.
Exits: BTC {'signal': 231, 'stop': 105}; ETH {'signal': 190, 'stop': 92}; HYPE {'signal': 213, 'stop': 88}. No max-hold exits on any coin.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$20,481.43; the $47.95 gap vs the -$9,566.52 closed-trade net is
mark-to-market on positions still open at the window end.

## Verdict: Loser — a clear, heavy loser on paper (−$9,566.52, PF 0.63, Sharpe −4.12).

VZO fires constantly on 1h crypto — 919 trades in ~8 months — and the
trend filter does not save it: the win rate is only 21.9% combined and
every coin loses, BTC worst at −$4,822.09 with a −48.9% drawdown. Unlike
a stop-dominated loser, most exits here are signal exits (634 of 919),
meaning the system itself keeps reversing out of trades at a loss: the
VZO cross back through 0 fires almost as soon as the entry cross does,
so entries are whipsawed in both directions. The oversold/overbought
reversal logic buys/sells into volume-confirmed moves that simply keep
going. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
