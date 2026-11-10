# Clenow Trend Following

Andreas Clenow's trend-following system from *Following the Trend*: trade only in the direction of the long-term trend, enter on a 50-day breakout, and let winners run until a 3x ATR trailing stop takes you out. Slow by design — on 1h crypto it fires only a handful of trades per coin over eight months.

## Rules

- Trend filter: EMA(1200) above EMA(2400) of close is bullish (50-day vs 100-day EMAs, 1 day = 24 bars); below is bearish. Equal EMAs are neutral — no entry.
- Long: close breaks above the highest high of the previous 1200 bars while bullish. Short: close breaks below the lowest low of the previous 1200 bars while bearish.
- Exit: the opposite breakout (a long exits on a new 1200-bar low while bearish, and vice versa), or the 3x ATR trailing stop — which does most of the exiting in practice. No take-profit target, no max hold.
- Risk: 30-day ATR (720 bars), 3x ATR stop/trail, 1% risk per trade, 3x leverage cap.
- All computation is causal, so signals on bar i use only data through bar i's close.

## Source

- Andreas Clenow, *Following the Trend* — trend filter 50/100 EMA cross, enter on 50-day extreme in trend direction, exit on 3x ATR trailing stop.
- Reference write-up: https://easylanguagemastery.com/strategies/free-trend-following-system-with-indicator-tracker/
- Clenow QuantCon keynote: https://www.slideshare.net/slideshow/the-quantcon-keynote-counter-trend-trading-threat-or-complement-to-trend-following-by-andreas-clenow-chief-investment-officer-of-acies-asset-management/68747586

Paper only, no live execution.
