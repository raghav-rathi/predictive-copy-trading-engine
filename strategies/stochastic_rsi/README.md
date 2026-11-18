# Stochastic RSI Cross

StochRSI(14,14,3,3) cross (Chande & Kroll): trade the %K/%D cross
only when it fires out of an extreme — longs out of oversold,
shorts out of overbought.

## Rules

- **Indicators:** RSI(14); StochRSI = (RSI − 14-bar min RSI) /
  (14-bar max RSI − 14-bar min RSI) × 100 (50.0 when the RSI range
  is 0); %K = SMA(3) of StochRSI; %D = SMA(3) of %K.
- **Long entry:** %K crosses above %D AND %K on the prior bar
  was < 20.
- **Short entry:** %K crosses below %D AND %K on the prior bar
  was > 80.
- **Long exit:** %K crosses below %D OR %K crosses above 80.
- **Short exit:** %K crosses above %D OR %K crosses below 20.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

All computation is causal: signals on bar i use only data through
bar i's close; crosses compare the current bar with the prior bar.

## Sources

- Chande & Kroll, StochRSI cross — https://doc.stocksharp.com/en/api-examples/0025_Stochastic_RSI_Cross
- StochRSI oscillator reference — https://www.multicharts.com/support/base/oscillators-gt-stoch-rsi/

Paper only, no live execution.
