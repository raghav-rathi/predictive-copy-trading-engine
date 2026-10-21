# OBV Divergence

Granville's On-Balance Volume meets classical price/oscillator
divergence: bet on a reversal only when volume pressure disagrees with
the price swing.

- **OBV:** `obv = cumsum(sign(c − c.shift(1)) * v)` — unchanged closes
  add 0. Volume flowing into up-closes accumulates, into down-closes
  drains.
- **Pivots** with confirmation lag k=10 (lookahead-free: a pivot at bar
  i is only readable at the close of bar i+k). Pivot low = unique
  minimum of `l[i−k..i+k]`; pivot high = unique maximum of `h`.
- **Bullish divergence:** new pivot low at a *lower* price than the
  previous pivot low, but OBV at the new pivot is *higher*. Enter long
  on the first bar after confirmation (i+k+1); skip if any divergence
  fired in the prior 15 bars (dedupe).
- **Bearish divergence:** mirror at pivot highs → short.
- **Exit:** long exits when a new pivot high prints (take the swing)
  or a bearish divergence confirms; shorts mirror.
- **Risk:** 1.5xATR stop (counter-trend entry, tight), 2.5xATR
  chandelier trail, 60-bar max hold, 1% risk/trade, 3x leverage.

Parameters: pivot_k=10, ATR(14). WARMUP=80.

Usage:

```python
from strategies.data import fetch_candles
from strategies.obv_divergence import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # pivot_k=10 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results (loser: -$551 combined on 49 trades — the
divergence is too rare on 1h bars to be tradeable) and CALIBRATION.md
for the 6/10/14 pivot-lag sensitivity check.
