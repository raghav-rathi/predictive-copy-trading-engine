# Bill Williams Market Facilitation Index Squat Breakout — Backtest

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
| BTC | 1027 | 29.8% | -8231.53 | -8.42 | -82.6% | -8.02 | 0.50 |
| ETH | 971 | 30.7% | -6651.41 | -4.82 | -69.4% | -6.85 | 0.65 |
| HYPE | 1018 | 38.6% | -4804.36 | -3.59 | -49.4% | -4.72 | 0.77 |
| **Combined** | **3016** | **33.1%** | **-19687.31** | **-7.21** | **-66.4%** | **-6.53** | **0.65** |

Fees: total $13841.93.
Exits: BTC {'signal': 775, 'stop': 252}; ETH {'signal': 720, 'stop': 251}; HYPE {'signal': 838, 'stop': 180}. No max-hold exits fired on any coin.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Heavy loser on paper (−$19,687.31, PF 0.65, Sharpe −7.21).

The squat breakout as specified trades far too often on 1h crypto: 3,016
trades in ~8 months, roughly one trade every 5–6 bars per coin. Squat bars
are common (~1,918–2,121 per coin, about a third of all bars), a breakout
close within 5 bars is the norm rather than the exception (~1,000 entry
signals per side per coin), and the FADE/EMA exit fires on ~58% of bars,
so positions last only a few bars on average. Every one of those
round-trips pays 0.11% in fees + slippage on up to 3x notional — $13,841.93
of fees in total — but the system loses before fees too (gross PnL
−$5,845.38), so this is not a cost problem alone: a 33.1% win rate with
PF 0.65 means the breakout direction after a squat carries no edge on
this window, and the quick FADE exit cuts winners as readily as losers.
BTC is the worst (−$8,231.53, −82.6% drawdown); HYPE is the least bad
(−$4,804.36, PF 0.77) and still deeply negative. Not a tradeable signal
as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Squat frequency on 1h crypto (~33% of bars) makes the "rare battle"
  framing from daily-bar Trading Chaos not transferable as-is; the
  5-bar breakout window is almost always satisfied, so the entry is
  effectively "any EMA-confirmed close beyond a recent range extreme".
- Never tune the shipped parameters on this window.

Paper only, no live execution.
