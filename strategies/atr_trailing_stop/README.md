# ATR Trailing Stop

Chuck LeBeau's Chandelier Exit: a trailing stop hung 3x ATR below the
highest high since the long regime started (mirrored for shorts: 3x
ATR above the lowest low since the short regime started). The stop
only ever ratchets in the trade's favour — up for longs, down for
shorts — so a pullback never loosens it. When the close crosses the
stop, the regime flips and a new trend leg begins.

## Rules

- **Long entry:** the regime flips long — the close crosses above the
  trailing stop from below.
- **Short entry:** the regime flips short — the close crosses below
  the trailing stop from above.
- **Long exit:** the regime flips short (same bar as a short entry).
- **Short exit:** the regime flips long (same bar as a long entry).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the regime flip. Max hold 120 bars.
- Parameters are the canonical Chandelier defaults (3x ATR(14));
  nothing was tuned to this window.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Chuck LeBeau, Chandelier Exit (popularised in Alexander Elder's
  *Come Into My Trading Room*, 2002): https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit

Paper only, no live execution.
