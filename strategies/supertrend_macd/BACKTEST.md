# Supertrend + MACD Agreement — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014. (The CSVs each
contain one further bar at exactly END_MS; the half-open window
excludes it. HYPE's cache starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 297 | 32.3% | -2579.00 | -1.65 | -33.9% | -8.68 | 0.78 |
| ETH | 298 | 32.6% | -1226.68 | -0.58 | -29.8% | -4.12 | 0.90 |
| HYPE | 301 | 31.9% | -768.59 | -0.29 | -19.6% | -2.55 | 0.94 |
| **Combined** | **896** | **32.3%** | **-4574.27** | **-1.14** | **-21.6%** | **-5.11** | **0.88** |

Fees: total $6775.74.
Exits: BTC {'stop': 174, 'signal': 123}; ETH {'stop': 200, 'signal': 98}; HYPE {'stop': 171, 'signal': 130}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$25,542.50.

## Verdict: LOSER — -$4,574.27 on 896 trades, combined Sharpe -1.14, MaxDD -21.6%.

All three coins lose, with profit factors 0.78–0.94 and win rates
~32% across the board — the Supertrend+MACD agreement filter does
not produce an edge on 1h crypto in this window; it fires ~300
trades per coin and the 2xATR stop ends more trades than the signal
exit on BTC and ETH (174/297 and 200/298 stops). Fees ($6,775.74)
exceed the net loss, so the strategy is underwater gross of costs
too. No parameter was tuned; the spec shipped as written, and the
calibration sweep (see CALIBRATION.md) found no alternate setting
that turns it green.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 896 trades is a decent sample, and all three coins agree in sign
  — the loss is a consistent result, not a one-coin artifact.
- The "first bar of agreement" entry and the histogram-sign exit
  are interpretation choices; see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
