# Markov Regime Switching — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

**HMM fits (first 1000 log returns per coin):**

| Coin | mu (calm, turb) | sigma (calm, turb) | A | pi |
|---|---|---|---|---|
| BTC | [-0.000106, 0.000467] | [0.002526, 0.006436] | [[0.9066, 0.0934], [0.1765, 0.8235]] | [0.0, 1.0] |
| ETH | [-0.000042, 0.000636] | [0.003415, 0.010785] | [[0.9179, 0.0821], [0.3002, 0.6998]] | [0.0, 1.0] |
| HYPE | [-0.000027, 0.000186] | [0.004815, 0.009529] | [[0.9447, 0.0553], [0.0527, 0.9473]] | [1.0, 0.0] |

Turbulent share post-warmup: BTC 18.6%, ETH 10.6%, HYPE 48.6%.
The high-vol sigma is 2.0–3.2x the calm sigma in every coin, so
the two states are genuinely separated by volatility, not by mean.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 159 | 35.2% | -1908.38 | -1.82 | -24.7% | -12.00 | 0.69 |
| ETH | 180 | 28.9% | -1695.50 | -1.54 | -24.5% | -9.42 | 0.75 |
| HYPE | 126 | 34.9% | -2031.79 | -2.21 | -23.9% | -16.13 | 0.61 |
| **Combined** | **465** | **32.7%** | **-5635.67** | **-2.80** | **-22.5%** | **-12.12** | **0.69** |

Fees: total $3700.15.
Exits: BTC {'stop': 109, 'signal': 50}; ETH {'stop': 100, 'signal': 80}; HYPE {'stop': 86, 'signal': 40}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24371.00 (closed-trade net -$5635.67; the $6.67 gap is open-position
mark-to-market at the window end).

## Verdict: LOSER — -$5,635.67 on 465 trades, combined Sharpe -2.80, MaxDD -22.5%.

The worst batch-35 result by a wide margin, and the loss is
uniform: all three coins lose with PF 0.61–0.75, so this is not
one bad coin. The regime switch does not save either system —
the calm EMA cross loses in chop and the turbulent RSI
mean-reversion loses when "turbulent" turns out to be the start
of a trend rather than a snap-back. The exit split (295 stops vs
170 signals) shows the stops doing most of the exiting, and the
-22.5% combined MaxDD is the deepest drawdown in the batch.
The HMM itself is not the failure — the fitted states are cleanly
vol-separated and the synthetic two-regime recovery test passes —
but clean vol classification does not imply the two attached
systems have edge. Regime-switching the system is not the same
as regime-switching the edge.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 465-trade sample, but the loss is consistent across all three
  coins — the negative result is the finding, not noise in one leg.
- The HMM is fit once on the first 1000 bars and never refit;
  if the vol regime structure drifts later in the window, the
  classifier goes stale (HYPE's 48.6% turbulent share vs ETH's
  10.6% hints the frozen fit behaves very differently per coin).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
