# Donchian + RSI — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 218 | 33.0% | -2503.78 | -1.63 | -26.6% | -11.49 | 0.75 |
| ETH | 198 | 35.4% | 745.67 | 0.56 | -16.9% | 3.77 | 1.08 |
| HYPE | 225 | 34.2% | -1300.68 | -0.72 | -23.4% | -5.78 | 0.89 |
| **Combined** | **641** | **34.2%** | **-3058.79** | **-0.77** | **-14.5%** | **-4.77** | **0.90** |

Fees: total $4928.75.
Exits: BTC {'stop': 212, 'signal': 6}; ETH {'stop': 192, 'signal': 6}; HYPE {'stop': 222, 'signal': 3}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,944.82 (closed-trade net -$3,058.79; the small gap to
$30,000 - $3,058.79 is unrealized PnL on positions still open at the
last bar).

## Verdict: LOSER — -$3,058.79 on 641 trades, combined Sharpe -0.77, MaxDD -14.5%.

The Donchian breakout fires far too often on 1h crypto: 641 trades,
the most of any system in the batch, and the RSI 55/45 confirmation
does not filter the whipsaws — BTC loses -$2,503.78 (Sharpe -1.63,
MaxDD -26.6%) and HYPE -$1,300.68, with only ETH positive (+$745.67,
PF 1.08). Win rate 34.2% with PF 0.90 means the winners never
outrun the losers, and $4,928.75 in fees is the largest fee drag in
the batch. The exit split is the story: only 15 of 641 trades end on
the opposite-Donchian signal exit; 626 end on the harness stop/trail,
so in practice this ships as a Donchian entry plus the 2xATR stop —
the channel exit is decorative because the stop is hit long before
price can break the opposite 20-bar extreme.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 641-trade sample: a real sample, but one window and two of three
  coins driving the loss — the edge is not universal across coins.
- The opposite-breakout exit almost never fires (15/641); the
  reported result is really the entry + harness stop/trail, not the
  Donchian system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
