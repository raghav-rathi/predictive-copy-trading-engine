# Climax Reversal — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 93 | 36.6% | -169.37 | -0.08 | -14.8% | -1.82 | 0.96 |
| ETH | 97 | 49.5% | 3997.97 | 2.73 | -9.1% | 41.22 | 1.84 |
| HYPE | 74 | 35.1% | -1245.54 | -1.56 | -19.5% | -16.83 | 0.65 |
| **Combined** | **264** | **40.9%** | **2583.06** | **1.21** | **-8.1%** | **9.78** | **1.20** |

Fees: total $2325.55.
Exits: BTC {'stop': 80, 'signal': 13}; ETH {'stop': 85, 'signal': 12}; HYPE {'stop': 67, 'signal': 7}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$32,583.06.

## Verdict: WINNER — +$2,583.06 on 264 trades, combined Sharpe 1.21, MaxDD -8.1%.

Wyckoff climaxes are a genuine winner on this window, but the win
is carried by one coin: ETH +$3,997.97 (win rate 49.5%, PF 1.84,
Sharpe 2.73, expectancy +$41.22/trade) does all the work, BTC is
essentially breakeven (-$169.37, PF 0.96), and HYPE loses
(-$1,245.54, PF 0.65, MaxDD -19.5%). Combined win rate 40.9% with
PF 1.20 clears $2,325.55 in fees and banks +$2,583.06 net, with a
mild combined MaxDD of -8.1%. The honest caveat is in the exit
split: only 32 of 264 trades ended on the opposite-climax signal
and 232 on the harness stop/trail, so the shipped system is
effectively a climax entry plus the 2xATR stop / 2.5xATR trail —
the opposite-climax exit is decorative in practice, and the edge
lives in the entry selectivity (a 2x volume spike with a weak
close at a fresh extreme is a rare, high-conviction bar).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 264-trade sample, and the result is one-coin driven (ETH) — BTC
  at breakeven and HYPE losing mean the edge is not universal
  across coins.
- The opposite-climax exit almost never fires (32/264); the
  reported result is really the entry + harness stop/trail, not
  the full climax-to-climax system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
