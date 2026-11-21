# Triple EMA Crossover — Backtest

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
| BTC | 179 | 23.5% | -1696.82 | -1.25 | -26.8% | -9.48 | 0.76 |
| ETH | 185 | 24.9% | -869.02 | -0.50 | -22.8% | -4.70 | 0.89 |
| HYPE | 175 | 24.0% | -2678.49 | -2.84 | -28.1% | -15.31 | 0.58 |
| **Combined** | **539** | **24.1%** | **-5244.33** | **-1.85** | **-23.8%** | **-9.73** | **0.75** |

Fees: total $4054.49.
Exits: BTC {'stop': 99, 'signal': 80}; ETH {'stop': 103, 'signal': 82}; HYPE {'signal': 88, 'stop': 87}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,755.67.

## Verdict: LOSER (worst of batch 42) — -$5,244.33 on 539 trades, combined Sharpe -1.85, MaxDD -23.8%.

All three coins lose, with the worst per-coin Sharpe in the batch
(HYPE -2.84, PF 0.58). The win rate is only 24.1% — the EMA(5) /
EMA(13) cross whipsaws in choppy 1h crypto, entering on crosses
that reverse within a few bars, and the cross-back exit then locks
in the small loss (250 of 539 exits are signal exits, the highest
signal-exit share in the batch). The EMA(50) stack filter does not
save it: most crosses that pass the filter still fail. No parameter
was tuned; the spec shipped as written. Note the calibration
alternate (9/21/55) was profitable — it was NOT adopted (see
CALIBRATION.md); adopting it would be PnL-selected tuning.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 539 trades is a solid sample and all three coins agree in sign —
  the loss is not a one-coin artifact.
- EMA cross systems are lagging by construction on 1h bars; the
  cross-back exit guarantees many small losses in range-bound
  stretches.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
