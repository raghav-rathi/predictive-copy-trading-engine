# Donchian ADX

Donchian 20 breakout (same entry as `donchian_channel`: close above the
prior 20-bar highest high / below the prior 20-bar lowest low) with a
Wilder ADX(14) > 25 trend filter, so breakouts are only traded while a
measurable trend is already in force.

## Rules

- **Long entry:** close above the prior 20-bar highest high AND
  ADX(14) > 25.
- **Short entry:** close below the prior 20-bar lowest low AND
  ADX(14) > 25.
- **Long exit:** ADX(14) falls below 20 OR the opposite breakout
  (close below the prior 20-bar lowest low).
- **Short exit:** ADX(14) falls below 20 OR the opposite breakout
  (close above the prior 20-bar highest high).
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

This is deliberately an ADX-filtered variant of `donchian_channel`
(precedent: `keltner_adx` vs `keltner_breakout`): the plain Donchian
breakout trades every 20-bar extreme, while this one skips breakouts
that fire in trendless chop and exits when trend strength decays even
if price has not reversed.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Donchian Channels: https://learn.tradelabsai.com/indicators/donchian-channels/
- Wilder ADX: https://www.investopedia.com/terms/a/adx.asp

Paper only, no live execution.
