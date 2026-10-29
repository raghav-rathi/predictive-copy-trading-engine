# Stochastic Pop

## Mechanism

Linda Raschke's Stochastic Pop (Street Smarts) is a
breakout-continuation setup, not a fade and not an oscillator
cross. The idea: when price breaks out of its recent range
while the fast stochastic is already pinned at an extreme, the
breakout has momentum behind it — the pop is the market
telling you the move is real, and the trade is to ride the
continuation for a short burst. That breakout requirement is
what separates it from `stoch_hook`, which trades a slow-K
cross against its trigger inside a trend bias with no breakout
at all:

- **fast %K(14):** 100 × (close − lowest low of 14) /
  (highest high of 14 − lowest low of 14).
- **Long pop:** fast %K crosses above 80 on the same bar that
  price closes above the prior 20-bar high (today excluded
  from the range, so it is a genuine new high).
- **Short pop:** fast %K crosses below 20 on the same bar
  that price closes below the prior 20-bar low.
- **Exit:** fast %K crosses back out of the extreme zone
  (below 80 for longs, above 20 for shorts) — the pop is
  spent. Pops are fast by nature, so the risk layer is tight
  as well: 1.5xATR stop, 2xATR trail, 3xATR target, 72-bar
  (3-day) max hold.

## Entry / exit rules

- Long entry: pop-up bar while flat.
- Short entry: pop-down bar while flat.
- Long exit: fast %K crosses back below 80. Short exit
  mirrors (cross back above 20).
- Risk layer: 1.5xATR stop, 2xATR trailing stop, 3xATR target,
  72-bar max hold, 1% risk per trade, 3x leverage cap.

## Source

Stochastic Pop (Linda Raschke, Street Smarts); fast-stochastic
construction per StockCharts ChartSchool
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-oscillators/stochastic-oscillator-fast-slow-and-full

## Honest caveats

- The backtest (see BACKTEST.md) loses overall (-$2,189 over
  373 trades) despite a green ETH leg (+$132). Fees are the
  story: $3,946 of fees on 373 trades — the pop exit fires
  fast (226 of 373 exits are signal exits), so the strategy
  churns.
- Requiring the %K cross and the breakout on the SAME bar is
  strict: on gradual breakouts %K is already above 80 when
  price finally breaks out, so the pop never registers. The
  same-bar rule is Raschke's, but it is a real miss rate.
- Paper/backtest only. Nothing here touches live execution.
