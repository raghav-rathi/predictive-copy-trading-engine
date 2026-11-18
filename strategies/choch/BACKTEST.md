# Change of Character (ChoCh) — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 88 | 38.6% | -566.49 | -0.89 | -7.4% | -6.44 | 0.74 |
| ETH | 83 | 45.8% | -412.52 | -0.65 | -10.9% | -4.97 | 0.81 |
| HYPE | 54 | 42.6% | -165.42 | -0.46 | -4.3% | -3.06 | 0.87 |
| **Combined** | **225** | **42.2%** | **-1144.43** | **-0.89** | **-6.3%** | **-5.09** | **0.80** |

Fees: total $1897.32.
Exits: BTC {'signal': 75, 'stop': 13}; ETH {'signal': 70, 'stop': 13}; HYPE {'signal': 47, 'stop': 7}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,855.57.

## Verdict: LOSER — -$1,144.43 on 225 trades, combined Sharpe -0.89, MaxDD -6.3%.

ChoCh is the least-bad loser of batch 39 but still a loser: 225
trades, a 42.2% win rate (the best of the three), PF 0.80, and
-$1,144.43 net after $1,897.32 in fees. No coin wins — BTC loses
-$566.49, ETH -$412.52, HYPE -$165.42 — but the drawdown is small
(-6.3% combined) because the signal exit cuts trades fast: 192 of
225 trades end on a signal exit vs only 33 on the stop. The
structure break is real (the close does break the protected level
on displacement), but on 1h crypto the break usually reverses back
through the last swing extreme within a few bars, so the trade is
exited for a small loss before any follow-through. Fees
($1,897.32) exceed the gross loss, so even a slightly better
follow-through would still have to clear the fee hurdle. No
parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 225 trades is a moderate sample; the loss is present on all
  three coins but the per-coin losses are small, so the verdict is
  "no edge" rather than "strongly negative".
- Mixed structure retains the previous trend (see CALIBRATION.md);
  the alternative reading (reset to 0) was not tested.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
