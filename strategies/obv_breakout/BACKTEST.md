# On-Balance Volume Breakout — Backtest

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
| BTC | 298 | 33.9% | -1476.91 | -0.67 | -32.1% | -4.96 | 0.89 |
| ETH | 317 | 33.1% | -149.22 | 0.07 | -24.8% | -0.47 | 0.99 |
| HYPE | 294 | 34.0% | -221.18 | 0.02 | -22.4% | -0.75 | 0.99 |
| **Combined** | **909** | **33.7%** | **-1847.30** | **-0.33** | **-20.9%** | **-2.03** | **0.96** |

Fees: total $6844.59.
Exits: BTC {'stop': 265, 'signal': 33}; ETH {'stop': 280, 'signal': 37}; HYPE {'stop': 271, 'signal': 23}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,152.70.

## Verdict: LOSER (near breakeven) — -$1,847.30 on 909 trades, combined Sharpe -0.33, MaxDD -20.9%.

The closest to breakeven in batch 42 (PF 0.96) but still red on all
three coins, and the most heavily traded strategy in the batch (909
trades, $6,844.59 of fees — fees alone exceed the loss, so gross of
fees the entries roughly break even). 816 of 909 exits are the
harness stop/trail, not the OBV signal exit (93): OBV breakouts do
not carry price far enough on 1h bars for the opposite OBV extreme
to exit the trade first. No parameter was tuned; the spec shipped
as written, and both calibration alternates lost more money (see
CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 909 trades is the largest sample in the batch, but PF 0.96 with
  all three coins red is a no-edge result, not a near-miss.
- OBV is cumulative from the window start, so its level depends on
  the arbitrary start date; only its 20-bar extremes are traded,
  which mitigates but does not remove the dependence.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
