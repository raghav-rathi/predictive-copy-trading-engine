# London Session Breakout — Backtest

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
| BTC | 109 | 40.4% | -1290.07 | -1.49 | -14.3% | -11.84 | 0.75 |
| ETH | 102 | 39.2% | 850.41 | 0.84 | -8.7% | 8.34 | 1.19 |
| HYPE | 134 | 41.0% | -1413.09 | -1.82 | -16.7% | -10.55 | 0.69 |
| **Combined** | **345** | **40.3%** | **-1852.76** | **-0.89** | **-10.4%** | **-5.37** | **0.87** |

Fees: total $2688.58.
Exits: BTC {'stop': 63, 'signal': 46}; ETH {'stop': 55, 'signal': 47}; HYPE {'signal': 73, 'stop': 61}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,147.24.

## Verdict: LOSER — -$1,852.76 on 345 trades, combined Sharpe -0.89, MaxDD -10.4%.

The London session breakout loses on 1h crypto: 345 trades, a 40.3%
win rate, PF 0.87, and -$1,852.76 net after $2,688.58 in fees. ETH
is the one winning coin (+$850.41, PF 1.19, Sharpe 0.84) but BTC
(-$1,290.07, PF 0.75) and HYPE (-$1,413.09, PF 0.69) more than
erase it. The exit split is nearly even (179 stop vs 166 signal):
about half the trades run into the 2xATR stop before the 16:00
time exit or the opposite-side break can save them, which is what
you expect when the overnight range break is a 24/7 crypto artifact
rather than a real London-open flow — there is no session open in
crypto, so the 08:00–12:00 window carries no special information.
No parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The fixed-UTC adaptation is the winter/GMT reading of the rule
  (see CALIBRATION.md); in summer months the shipped window is
  effectively one hour earlier in London terms.
- The published 1R target is not implemented (see CALIBRATION.md);
  the 2xATR stop / 2.5xATR trail stand in for the range-other-side
  stop.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
