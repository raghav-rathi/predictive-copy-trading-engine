# Aroon Cross

## Mechanism

Tushar Chande's Aroon (1995) measures trend by time, not
price distance: how recently did price print a new high or
low within the last 25 bars?

- **Aroon Up** = 100 × (25 − bars since 25-bar high) / 25.
  A new high on the current bar scores 100; a high 25 bars
  ago scores 0.
- **Aroon Down** = 100 × (25 − bars since 25-bar low) / 25.
- **Long entry:** Aroon Up crosses above Aroon Down while
  Aroon Up > 70 (a high within roughly the last 7 bars).
- **Short entry:** Aroon Down crosses above Aroon Up while
  Aroon Down > 70.
- **Exit:** the opposite cross, ungated.

The > 70 gate is the spec's strength filter: a bare cross
can happen when both lines are drifting in the 40s during a
range; requiring the crossing line above 70 means fresh
extremes are actually being made.

## Entry / exit rules

- Long entry: Aroon Up cross above Aroon Down, Aroon Up > 70.
- Short entry: Aroon Down cross above Aroon Up, Aroon Down > 70.
- Long exit: Aroon Down cross above Aroon Up. Short exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Aroon, StockCharts ChartSchool (Tushar Chande, 1995)
https://school.stockcharts.com/doku.php?id=technical_indicators:aroon
— verified: Aroon Up/Down from bars since the 25-period
high/low, 0–100 scale, default period 25.

## Honest caveats

- The backtest (see BACKTEST.md) is flat, not a win:
  +$119 combined over 588 trades on $30k capital (Sharpe
  +0.11) — noise. ETH and HYPE are mildly green, BTC loses
  $1,676, and $5,193 in fees consumed most of the gross
  edge. 516 of 588 exits are stops: the cross fires, price
  usually fails to follow through before the 2xATR stop.
- Paper/backtest only. Nothing here touches live execution.
