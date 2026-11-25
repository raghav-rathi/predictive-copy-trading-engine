# Ichimoku Kumo Breakout

Goichi Hosoda's Ichimoku Kinkō Hyō (1930s, published late
1960s): trade the breakout of price through the Kumo cloud,
with tenkan/kijun agreement as the momentum filter.

- **Long:** close crosses above the cloud top
  (max(senkou_a, senkou_b)) AND tenkan > kijun
- **Short:** close crosses below the cloud bottom
  (min(senkou_a, senkou_b)) AND tenkan < kijun
- **Exit:** close crosses back into the cloud — long exits
  when close < cloud top, short exits when close > cloud
  bottom
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold (cloud trades run longer), 1% risk/trade, 3x
  leverage (the harness stops sit behind the cloud exit as
  a safety net for gap-through-cloud moves)

Parameters: tenkan 9, kijun 26, senkou 52 — the Hosoda
standard. Senkou A = (tenkan + kijun)/2 plotted 26 bars
ahead; Senkou B = (highest high(52) + lowest low(52))/2
plotted 26 bars ahead. The chikou span is NEVER read: it is
close shifted −26 (lookahead). The cloud read at bar i was
computed from data through bar i−26, so it is known at bar i.

Usage:

```python
from strategies.ichimoku_kumo_breakout import indicators, signals, risk

df = indicators.add_indicators(df)  # tenkan=9, kijun=26, senkou=52 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results and
CALIBRATION.md for the senkou-period 26/52/78 sensitivity
check and the lookahead audit. No parameter was tuned to PnL.

Source: Wikipedia, "Ichimoku Kinkō Hyō" —
https://en.wikipedia.org/wiki/Ichimoku_Kink%C5%8D_Hy%C5%8D
(verified via search 2026-11-25; confirms Hosoda as the
developer, tenkan (9) / kijun (26) / senkou A and B (52,
plotted 26 ahead) formulas, the Kumo as the space between
the senkou spans, and chikou as today's close projected
back 26 periods — hence excluded here).
