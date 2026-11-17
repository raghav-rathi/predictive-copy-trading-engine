# Triple RSI

Three Wilder RSIs at different speeds must agree before a trade
fires: RSI(7), RSI(14) and RSI(21) all above 55 for a long, all
below 45 for a short. The entry triggers on the bar the last of
the three crosses its threshold — the moment of full agreement.
Any single RSI crossing back through 50 exits the trade.

## Rules

- **RSI(7), RSI(14), RSI(21)** — Wilder-smoothed, on the close.
- **Long entry:** all three RSIs > 55, triggered on the bar the
  last of the three crosses above 55 (the first bar on which all
  three are above 55 after at least one was at or below 55).
- **Short entry:** all three RSIs < 45, triggered on the bar the
  last of the three crosses below 45.
- **Long exit:** any RSI crosses below 50.
- **Short exit:** any RSI crosses above 50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The entry fires once per alignment, not on every bar the three
stay aligned, and it never fires on bar 0 (there is no previous
bar to cross from). All computation is causal, so signals on bar
i use only data through bar i's close.

## Source

- Triple-RSI momentum confirmation (RSI 7/14/21 with 55/45
  entry thresholds and a 50 exit): a standard multi-timeframe RSI
  agreement setup; RSI definition per Investopedia:
  https://www.investopedia.com/terms/r/rsi.asp

Paper only, no live execution.
