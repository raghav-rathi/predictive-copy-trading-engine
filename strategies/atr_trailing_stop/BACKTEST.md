# ATR Trailing Stop — Backtest

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
| BTC | 248 | 35.1% | -643.72 | -0.25 | -26.5% | -2.60 | 0.94 |
| ETH | 251 | 38.6% | 1723.42 | 1.01 | -18.7% | 6.87 | 1.14 |
| HYPE | 207 | 35.7% | 1303.63 | 0.92 | -18.1% | 6.30 | 1.12 |
| **Combined** | **706** | **36.5%** | **2383.33** | **0.69** | **-11.4%** | **3.38** | **1.07** |

Fees: total $6028.95.
Exits: BTC {'stop': 232, 'signal': 16}; ETH {'stop': 234, 'signal': 17}; HYPE {'stop': 198, 'signal': 9}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$32,448.03 (closed-trade net +$2,383.33; the $64.70 gap is unrealised
MTM on positions still open at the window end).

## Verdict: WINNER — +$2,383.33 on 706 trades, combined Sharpe 0.69, MaxDD -11.4%.

The Chandelier-style trailing stop is the second winner of this batch
and the strongest by combined dollars: ETH +$1,723.42 (Sharpe 1.01,
PF 1.14) and HYPE +$1,303.63 (Sharpe 0.92, PF 1.12) carry the book
while BTC roughly breaks even (-$643.72, PF 0.94). Win rate 36.5% with
PF 1.07 clears $6,028.95 in fees and banks +$2,383.33 net. The honest
caveat is in the exit split: 664 of 706 trades ended on the harness
stop/trail and only 42 on the regime flip, so the shipped system is
effectively a 3xATR-trailing-stop regime entry plus the 2xATR stop /
2.5xATR trail — the 2xATR harness stop sits inside the 3xATR
Chandelier stop, so it almost always fires first, and the regime flip
itself is decorative as an exit. The edge lives in the entry
selectivity: a flip only happens after a full 3xATR move against the
old regime, so entries arrive on confirmed trend changes rather than
on every oscillator wiggle (706 trades vs the MACD cross's 1,280).
MaxDD -11.4% on the combined curve is the mildest of the three
strategies in this batch.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 706-trade sample: a real sample, but one window and two of three
  coins driving the result — BTC's near-breakeven loss is a reminder
  the edge is not universal across coins.
- The regime-flip exit almost never fires (42/706); the reported
  result is really the Chandelier entry + harness stop/trail, not
  LeBeau's full system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
