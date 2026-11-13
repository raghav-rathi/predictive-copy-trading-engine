# Pairs Spread (BTC-ETH) — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**This is a single spread book, not per-coin.** The BTC and ETH
legs are combined into one synthetic spread instrument (USD spread
OHLC = BTC o/h/l/c − beta × ETH o/h/l/c, beta the trailing 500-bar
OLS hedge ratio, volume = BTC volume) and the harness runs ONCE on
it. There is no per-coin table for this strategy; the one row
below is the whole result.

**Bar counts used:** BTC 5847, ETH 5847, spread bars 5847.

## Results (shipped config)

| Instrument | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| SPREAD | 38 | 28.9% | -1148.67 | -1.76 | -16.6% | -30.23 | 0.49 |

Fees: total $459.73.
Exits: SPREAD {'stop': 36, 'signal': 2}.
Sharpe -1.76, MaxDD -16.62%. Start equity $10000.00, end equity
$8851.33.

## Verdict: LOSER — -$1,148.67 on 38 trades, Sharpe -1.76, MaxDD -16.6%.

The BTC-ETH spread does not mean-revert on this window the way
GGR pairs do: only 2 of 38 trades ended on the z-cross-0 signal
exit while 36 ended on the harness stop, i.e. dislocations kept
running against the position instead of snapping back. Win rate
28.9% and PF 0.49 lose money even before the $459.73 in fees, and
expectancy -$30.23 per trade is the worst per-trade figure in
this batch. The honest read is that a 500-bar OLS beta on two
trending crypto majors leaves a spread that still trends — the
hedge ratio drifts, the "equilibrium" moves, and a ±2 entry is
catching a regime shift, not a dislocation. The 38-trade sample
is small, but the exit split (36 stops vs 2 signals) is the
systematic tell: the mean-reversion premise fails here.

## Limitations

- Single ~8-month crypto window; funding unmodeled (a real
  pairs book pays/receives funding on both legs); next-bar-open
  execution vs idealized entry.
- 38-trade sample: small, and every trade is the same single
  spread — no diversification at all.
- The USD spread ATR stop is an approximation: a real pairs book
  would stop each leg separately and size by spread volatility,
  not by the synthetic instrument's ATR.
- The spread is built with beta recomputed each bar, so the
  instrument itself changes definition as beta drifts.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
