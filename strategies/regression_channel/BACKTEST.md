# Linear Regression Channel — Backtest

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
| BTC | 163 | 39.9% | -3264.53 | -3.74 | -36.5% | -20.03 | 0.57 |
| ETH | 150 | 48.0% | -1598.67 | -1.55 | -22.6% | -10.66 | 0.77 |
| HYPE | 169 | 42.6% | -1413.84 | -1.32 | -25.0% | -8.37 | 0.81 |
| **Combined** | **482** | **43.4%** | **-6277.04** | **-3.08** | **-26.5%** | **-13.02** | **0.71** |

Fees: total $3088.50.
Exits: BTC {'stop': 99, 'signal': 64}; ETH {'stop': 84, 'signal': 66}; HYPE {'stop': 103, 'signal': 66}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$23,864.03 (closed-trade net -$6,277.04; the small gap to
$30,000 - $6,277.04 is unrealized PnL on positions still open at the
last bar).

## Verdict: LOSER — -$6,277.04 on 482 trades, combined Sharpe -3.08, MaxDD -26.5%.

The worst system of the batch by dollars and by Sharpe. Mean
reversion into the regression midline fails on 1h crypto: all three
coins lose (BTC -$3,264.53 with Sharpe -3.74 and MaxDD -36.5%, ETH
-$1,598.67, HYPE -$1,413.84), win rate 43.4% with PF 0.71 means the
losers are both more frequent in dollars and larger. The exit split
is the one healthy sign — 196 of 482 trades (40.7%) end on the
midline signal exit, so the reversion leg does complete often — but
the entries buy into moves that keep trending: a "cross back inside
the band" on a 100-bar channel is usually a pause inside a trend,
not a reversal, and the 2xATR stop then takes the trade out before
the midline pays. Combined MaxDD -26.5% is the deepest in the batch.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 482-trade sample: a real sample, but one window — the loss is
  consistent across all three coins, which is stronger evidence
  against the mechanism than a single-coin loss would be.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
