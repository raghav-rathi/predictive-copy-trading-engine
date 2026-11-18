# ATR Expansion Breakout

Trade a close beyond a tight 20-bar close range — but only when
volatility is expanding (ATR above its 20-bar average). The range
must be tight (width <= 2xATR) and the break must clear the level
by 0.25xATR.

## Rules

- **Indicators:** ATR(14); ATR_MA20 = SMA(20) of ATR; range high /
  low = max / min close of the previous 20 bars; range width =
  high − low; range_ok = width <= 2.0 × ATR.
- **Long entry:** close > range_high + 0.25×ATR AND ATR > ATR_MA20
  AND range_ok.
- **Short entry:** close < range_low − 0.25×ATR AND ATR > ATR_MA20
  AND range_ok.
- **Long exit:** close < range_high (back inside the range) OR
  ATR < ATR_MA20.
- **Short exit:** close > range_low OR ATR < ATR_MA20.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The range levels use the previous 20 bars only (shifted by 1), so
a close can actually break them. All computation is causal:
signals on bar i use only data through bar i's close.

## Sources

- Rule-based breakout blueprint — https://www.steadypips.net/guides/breakout-trading-strategy-rule-based-blueprint/
- ATR volatility breakout — https://arconomy.app/blog/2026-05-14-us500-atr-volatility-breakout

Paper only, no live execution.
