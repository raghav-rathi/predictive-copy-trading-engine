# Relative Vigor Index — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795269600000) (2026-03-14 22:00 UTC →
2026-11-21 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6040, ETH 6040, HYPE 6038.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1733 | 31.1% | -9292.48 | -10.84 | -93.2% | -5.36 | 0.54 |
| ETH | 1767 | 35.9% | -8340.48 | -7.17 | -83.7% | -4.72 | 0.65 |
| HYPE | 1748 | 38.6% | -8163.46 | -7.71 | -82.4% | -4.67 | 0.63 |
| **Combined** | **5248** | **35.2%** | **-25796.42** | **-10.82** | **-86.4%** | **-4.92** | **0.61** |

Fees: total $17127.83.
Exits: BTC {'signal': 1366, 'stop': 367}; ETH {'signal': 1426, 'stop': 341}; HYPE {'signal': 1471, 'stop': 277}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$4,237.51.

## Verdict: LOSER (worst of the batch) — -$25,796.42 on 5248 trades, combined Sharpe -10.82, MaxDD -86.4%.

All three coins lose 82–93% of starting equity. RVI crosses its
signal line almost every other bar on 1h crypto (~1 trade per 3.5
bars per coin), so the strategy is a pure churn machine: 5248 trades,
$17,128 of fees. Gross PnL before fees is about -$8,669, so unlike
the other two strategies in this batch the entries are negative
before costs too — the 4-bar RVI whipsaws and the cross entries buy
tops and sell bottoms at this frequency. Most trades (4263 of 5248)
exit on the opposite cross within a few bars. No parameter was
tuned; the spec shipped as written, and both calibration alternates
lost money (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 5248 trades is a very large sample, but it is one window and three
  correlated coins — the loss is a property of crossover churn plus
  fees, not a small-sample fluke.
- The direct 4-bar SWMA ratio (no 10-bar smoothing) is noisier than
  the platform variant; the smoothed alternate also loses (see
  CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
