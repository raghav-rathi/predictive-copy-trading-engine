# Percentage Volume Oscillator

PVO (12, 26, 9): the MACD of volume — 100*(EMA12(v)-EMA26(v))/EMA26(v) with a 9-period signal line. Long on a PVO cross above its signal line while price holds above SMA(50); short on a cross below while price holds below SMA(50); exit on the opposite cross.

## Rules

- Long: PVO crosses above its signal line and close > SMA(50).
- Short: PVO crosses below its signal line and close < SMA(50).
- Exit: opposite PVO/signal cross (plus ATR stop / trail).

## Source

- Percentage Volume Oscillator (StockCharts ChartSchool): https://chartschool.stockcharts.com/~gitbook/pdf?page=AujMj8CJKpAa7EHWRU4k&only=yes&limit=100

Paper only, no live execution.
