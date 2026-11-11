# Wilder Volatility System — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794402000000) (2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5776, ETH 5776, HYPE 5774.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 177 | 31.1% | -966.72 | -0.56 | -21.0% | -5.46 | 0.89 |
| ETH | 181 | 39.2% | 1920.69 | 1.24 | -14.3% | 10.61 | 1.23 |
| HYPE | 132 | 39.4% | 2803.99 | 1.92 | -10.1% | 21.24 | 1.43 |
| **Combined** | **490** | **36.3%** | **3757.96** | **1.20** | **-8.0%** | **7.67** | **1.16** |

Fees: total $4355.00.
Exits: BTC {'stop': 174, 'signal': 3}; ETH {'stop': 176, 'signal': 5}; HYPE {'stop': 131, 'signal': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$33,757.96.

## Verdict: WINNER — +$3,757.96 on 490 trades, combined Sharpe 1.20, MaxDD -8.0%.

The one genuine winner of batch 33. Wilder's ATR-breakout entry works
on 1h crypto where the cross and Donchian systems failed: HYPE
+$2,803.99 (Sharpe 1.92, PF 1.43) and ETH +$1,920.69 (Sharpe 1.24,
PF 1.23) carry the book, and only BTC loses (-$966.72, PF 0.89). Win
rate 36.3% with PF 1.16 means the winners outrun the losers by enough
to clear $4,355.00 in fees and still bank +$3,757.96 — the system is
profitable net, not just gross. The honest caveat is in the exit
split: 481 of 490 trades ended on the harness stop/trail and only 9
on the reverse trigger, so the shipped system is effectively an
ATR-breakout entry plus the 2xATR stop / 2.5xATR trail — the reverse
signal is decorative in practice, and the edge lives in the entry
selectivity (a close beyond prev high/low + a full ATR(7) is a much
rarer, stronger event than a moving-average cross). MaxDD -8.0% on the
combined curve is also the mildest in the batch.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 490-trade sample: a real sample, but one window and two of three
  coins driving the result — BTC's loss is a reminder the edge is
  not universal across coins.
- The reverse-trigger exit almost never fires (9/490); the reported
  result is really the entry + harness stop/trail, not Wilder's
  full system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
