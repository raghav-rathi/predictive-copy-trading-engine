# Relative Strength Breakout

## Mechanism

The relative-strength ratio line R = coin close / BTC close
measures whether a coin is outperforming or underperforming
Bitcoin, independent of Bitcoin's own direction. This engine
trades breakouts of the ratio line's own recent range —
distinct from relative_momentum_index (an RSI variant on the
coin alone): here the signal lives entirely in the coin-vs-BTC
ratio, so a coin can trigger a long even while Bitcoin falls,
provided it falls less.

- **Ratio line:** R = coin close / BTC close, BTC closes
  aligned on timestamp `t`, forward-filled across any missing
  BTC bar (causal).
- **Breakout:** R above its prior 20-bar high (prior bars
  only — the current bar is excluded, so the test is causal)
  = long; R below its prior 20-bar low = short.
- **Exit:** R fades back through its 20-bar mean = the
  out/underperformance has faded.

## Benchmark sourcing

`add_indicators(df, benchmark_df=None)` resolves the BTC
benchmark in this order: (1) an explicitly passed benchmark
frame (columns t, c) — the path the unit tests exercise, and
what a driver should use when it already holds BTC candles;
(2) otherwise the shipped cache, read-only, at
`data/candles/BTC_1h.csv` — this keeps the standard
single-frame harness working, since SPEC.add_indicators takes
one frame. `signals.add_signals_with_benchmark(df, btc_df)`
is a convenience wrapper for path (1). There is deliberately
NO fallback proxy: a coin-vs-its-own-SMA ratio is not a
relative-strength line, and if neither source is available
the loader raises ValueError instead of silently
substituting one. The loader also dedupes the benchmark on
`t` — the shipped BTC cache carries 5 duplicated timestamps
(exact duplicate rows), which would otherwise multiply rows
in the join.

## Entry / exit rules

- Long entry: ratio breaks above its prior 20-bar high while flat.
- Short entry: ratio breaks below its prior 20-bar low while flat.
- Long exit: ratio falls below its 20-bar mean while long.
  Short exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trail, 168-bar max hold,
  1% risk per trade, 3x leverage cap.

## Source

Relative strength ratio line (Mansfield relative strength) —
Investopedia
https://www.investopedia.com/terms/r/relativestrength.asp

## Honest caveats

- The backtest (see BACKTEST.md) loses: -$3,610 across 531
  traded-leg trades (ETH -$2,559, HYPE -$1,051). The BTC leg
  is the benchmark by construction (ratio = 1, flat range)
  and correctly produces zero trades; it is excluded from
  the combined total, not counted as a flat leg.
- 334 of 531 traded-leg trades end on the stop, not the
  mean-fade exit: ratio breakouts on 1h mostly fail back
  through the stop before the mean exit can rescue them.
- Paper/backtest only. Nothing here touches live execution.
