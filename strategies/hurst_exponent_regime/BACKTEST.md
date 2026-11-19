# Hurst Exponent Regime Switch — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 79 | 38.0% | -1179.79 | -1.34 | -15.4% | -14.93 | 0.65 |
| ETH | 91 | 34.1% | 226.52 | 0.30 | -12.8% | 2.49 | 1.05 |
| HYPE | 86 | 38.4% | 1540.59 | 1.32 | -8.1% | 17.91 | 1.37 |
| **Combined** | **256** | **36.7%** | **587.32** | **0.33** | **-6.6%** | **2.29** | **1.05** |

Fees: total $2211.68.
Exits: BTC {'stop': 68, 'signal': 11}; ETH {'stop': 72, 'signal': 19}; HYPE {'stop': 74, 'signal': 12}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30,587.32.

## Verdict: NOMINAL WINNER (thin) — +$587.32 on 256 trades, combined Sharpe 0.33, MaxDD -6.6%, PF 1.05.

The combined row is barely green and should not be read as an
edge: the entire profit is HYPE (+$1,540.59, PF 1.37), ETH is
near-flat (+$226.52, PF 1.05), and BTC loses (-$1,179.79,
PF 0.65). Win rate is 36.7% with expectancy +$2.29/trade
against $2,211.68 of fees — the gross edge is small and the
result is statistically indistinguishable from luck. Most
exits (214 of 256) are the harness stop/trail, not signal exits.

One structural fact matters more than the PnL: the R/S
estimator reads H ≈ 0.59 on average, so the mode sits in trend
72–75% of the time and in reversion only ~1% of bars on all
three coins. On this window the strategy is effectively a
trend-only EMA-cross system; the reversion leg (RSI fades) is
essentially untested in live conditions. No parameter was tuned;
the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- R/S Hurst on a 200-bar window is noisy and biased upward at
  these scales (white noise reads ~0.6), which is why the trend
  band dominates; see CALIBRATION.md.
- The combined win rests on HYPE alone; BTC loses.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
