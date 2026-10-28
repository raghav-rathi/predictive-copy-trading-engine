# PPO Signal Cross

## Mechanism

The Percentage Price Oscillator restates the MACD as a percentage of price: PPO = (EMA(12) − EMA(26)) / EMA(26) × 100, with an EMA(9) signal line. Normalising by price makes oscillator readings comparable across coins at very different price levels (a $70k BTC vs a $20 HYPE) and across regimes within one coin. The strategy trades the PPO/signal-line cross, the direct analogue of the classic MACD signal cross.

## Entry / exit rules

- **Long entry:** PPO crosses above its EMA(9) signal line.
- **Short entry:** PPO crosses below its EMA(9) signal line.
- **Long exit:** PPO crosses back below its signal line.
- **Short exit:** PPO crosses back above its signal line.

Signals execute at the next bar's open; one position at a time per coin.

## Risk

2xATR stop, 2.5xATR chandelier trail, no fixed target, 168-bar (7-day) max hold, 1% risk/trade, 3x leverage cap.

## Source

Percentage Price Oscillator (StockCharts ChartSchool) — https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo

## Honest caveats

- The signal-line cross is the fastest trigger in this batch and it shows: 1,221 trades, the most of any batch-19 strategy, and the worst combined result.
- A cross of a smoothed oscillator against its own smoothing is inherently whipsaw-prone in chop; BTC (−$4,882, max DD −51.2%) and ETH (−$3,152) both bleed steadily.
- HYPE is barely green (+$282, PF 1.02) — a coin flip, not confirmation.
- Single 7-month crypto window; funding unmodeled; next-bar-open execution vs idealized entry.
