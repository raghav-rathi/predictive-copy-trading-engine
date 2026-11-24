# Ichimoku + Stochastic

Ichimoku cloud trend filter with a Stochastic cross trigger:
trade only in the cloud's direction, and only when the
Stochastic turns from an extreme.

## Rule

```
LONG when, on the same bar:
  close > cloud top (max of Senkou A/B),
  Tenkan > Kijun,
  %K crosses above %D while %K < 30.
SHORT is the mirror:
  close < cloud bottom (min of Senkou A/B),
  Tenkan < Kijun,
  %K crosses below %D while %K > 70.
```

- **Ichimoku (9/26/52):** Tenkan-sen is the 9-bar high/low
  midpoint, Kijun-sen the 26-bar midpoint, Senkou A the
  (Tenkan + Kijun) / 2 shifted +26 bars, Senkou B the 52-bar
  midpoint shifted +26 bars. The shifted Senkou values read
  at bar *i* derive from data through bar *i*−26, so reading
  them at bar *i* is causal — this is the historical cloud,
  not the projected cloud 26 bars ahead.
- **Stochastic (14,3,3):** %K = 100 × (close − lowest close
  of last 14) / (highest − lowest close of last 14); %D is
  the 3-bar SMA of %K. A flat 14-bar range defines %K = 50.
- **Exit long:** %K crosses below %D, OR close falls back
  to/below the cloud top (back inside or through the cloud).
  **Exit short:** the mirror.
- **Chikou Span is NOT used:** `base.ichimoku` defines it as
  `close.shift(-26)`, which looks 26 bars into the future.
  It is not computed or exposed here.
- **Max hold:** 120 bars (~5 days on 1h).

## Honest flag: exits fire almost immediately

On the batch-45 window the median hold is 2 bars on every
coin — the close-back-into-cloud exit triggers almost as soon
as the trade starts, because the Stochastic cross that fires
the entry usually happens while price is still hugging the
cloud edge. The system therefore pays entry costs for a
2-hour hold far more often than it rides a cloud trend leg.
See BACKTEST.md.

## 1h scaling notes

- The cloud is a slow filter (52 + 26 bars to form); the
  Stochastic is a fast trigger. On 1h bars the two disagree
  constantly: price crosses the cloud edge and the Stochastic
  whipsaws across %D several times a day, so the entry gate
  (%K < 30 / > 70) does most of the filtering and still lets
  through ~1 trade per coin per 3 days.

## Risk

2×ATR(14) harness stop, 3×ATR chandelier trail, no target,
120-bar (~5-day) max hold, 1% risk per trade, 3× leverage
cap. WARMUP = 80 bars (52-bar Senkou B + 26-bar shift, plus
margin).

Source: Ichimoku Kinko Hyo (Goichi Hosoda) + Stochastic
Oscillator (George Lane)
(https://www.investopedia.com/terms/i/ichimoku-cloud.asp).
