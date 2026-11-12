# MACD Histogram — Backtest

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
| BTC | 428 | 31.1% | -4312.55 | -2.74 | -49.5% | -10.08 | 0.72 |
| ETH | 422 | 31.8% | -1985.97 | -0.90 | -41.7% | -4.71 | 0.87 |
| HYPE | 432 | 34.3% | 1955.18 | 1.09 | -16.5% | 4.53 | 1.10 |
| **Combined** | **1282** | **32.4%** | **-4343.34** | **-0.89** | **-24.4%** | **-3.39** | **0.91** |

Fees: total $9068.15.
Exits: BTC {'stop': 259, 'signal': 169}; ETH {'stop': 271, 'signal': 151}; HYPE {'stop': 250, 'signal': 182}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$25,869.81 (vs $30,000 + net −$4,343.34 = $25,656.66; the $213.15 gap
is the mark-to-market of positions still open at the window end —
verified on BTC, where a short entered on the last histogram cross
was still open at the final bar).

## Verdict: LOSER — −$4,343.34 on 1,282 trades, combined Sharpe −0.89, MaxDD −24.4%.

The MACD histogram zero cross loses overall, and badly on BTC
(−$4,312.55, Sharpe −2.74, MaxDD −49.5%). Only HYPE wins (+$1,955.18,
PF 1.10) and it cannot carry the book. 1,282 trades is the largest
sample of any strategy this batch and the verdict is unambiguous:
the histogram cross fires constantly in a range — 502 of the 1,282
trades did end on the opposite cross, so the signal exit does real
work here, unlike the breakout systems — but the cross is a lagging
momentum flip, not a trend change, and on 1h crypto it buys the top
of every chop and sells the bottom. Fees alone were $9,068.15,
more than double the net loss; even gross of fees the system barely
breaks even. BTC's −49.5% MaxDD is the worst single-coin drawdown
in the batch.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,282-trade sample: large, and the loss is driven by BTC and ETH
  while HYPE wins — the edge, if any, is coin-specific, not
  universal.
- The histogram cross is a signal-line cross, not the MACD-line zero
  cross; the MACD-line zero cross (12/26 EMA cross) is a slower,
  different signal and was not tested.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
