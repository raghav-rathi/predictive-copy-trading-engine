# Raschke 3-Bar Triangle

Linda Raschke's 3-bar triangle: an inside-bar contraction defines
a small 3-bar range; a directional break of that range on
expanding volume is the entry.

## Rules

- **Contraction bar:** h[i] < max(h[i-1], h[i-2]) AND
  l[i] > min(l[i-1], l[i-2]) — "high below two day high and low
  above two day low". Triangle high = max(h[i-2], h[i-1], h[i]);
  triangle low = min(l[i-2], l[i-1], l[i]).
- **Long entry:** within 5 bars after a contraction bar, close
  breaks above the triangle high AND volume > 1.25x SMA(v, 20).
- **Short entry:** mirror — close below the triangle low with
  volume expansion.
- **Long exit:** close back below the triangle low (failed
  breakout) OR an opposite triangle signal.
- **Short exit:** close back above the triangle high OR an
  opposite triangle signal.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The triangle levels are forward-filled for 5 bars after the
contraction bar; a new contraction inside the window restarts the
triangle and the 5-bar clock. The contraction bar itself can never
trigger an entry (its close sits inside its own triangle). All
computation is causal, so signals on bar i use only data through
bar i's close.

## Sources

- New Trader U, "Market Wizard Linda Raschke Trading Strategy":
  https://www.newtraderu.com/2022/08/25/market-wizard-linda-raschke-trading-strategy/
- cTrader, 3-bar triangle indicator:
  https://ctrader.com/products/47

Paper only, no live execution.
