# Dual Momentum — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. The three coins are aligned on the union
of timestamps for the basket (closes forward-filled across the odd
missing bar); each coin is then backtested on its own bars.
$10k start per coin, 1% risk per trade on the 2xATR stop, 3x
leverage cap, 0.045% fee + 0.01% slippage per side, funding off,
max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 91 | 42.9% | 117.08 | 0.21 | -10.2% | 1.29 | 1.04 |
| ETH | 138 | 33.3% | -639.63 | -0.75 | -12.9% | -4.63 | 0.83 |
| HYPE | 142 | 36.6% | 1253.77 | 1.39 | -6.5% | 8.83 | 1.32 |
| **Combined** | **371** | **36.9%** | **731.23** | **0.55** | **-5.3%** | **1.97** | **1.07** |

Fees: total $3088.27.
Exits: BTC {'signal': 54, 'stop': 37}; ETH {'signal': 96, 'stop': 42}; HYPE {'signal': 93, 'stop': 49}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30714.01 (closed-trade net +$731.23; the $17.22 gap is open-position
mark-to-market at the window end).

## Verdict: WINNER (marginal) — +$731.23 on 371 trades, combined Sharpe 0.55, MaxDD -5.3%.

Dual momentum banks a small profit, carried entirely by HYPE
(+$1,253.77, Sharpe 1.39, PF 1.32); BTC is breakeven (+$117.08,
PF 1.04) and ETH loses (-$639.63, PF 0.83). Win rate 36.9% with
PF 1.07 barely clears $3,088.27 in fees, so the edge is thin: one
coin driving the result and a profit factor only just above 1.0
means this reads as a weak positive, not a robust system. The
exit split is informative — 243 of 371 trades ended on the
rank/momentum signal exit and only 128 on the stop, so unlike
most batches the system-defined exit actually does the work here.
MaxDD -5.3% on the combined curve is mild, consistent with the
absolute-momentum leg keeping the book flat in downtrends.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 371-trade sample, but PF 1.07 is within noise of breakeven and
  two of three coins do not win — do not mistake this for a
  validated edge.
- Antonacci's system holds one winner and rotates monthly; this
  adaptation trades each coin independently on hourly bars, so it
  can hold offsetting long/short legs across coins at once.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
