# Sine-Weighted MA Trend

Fast/slow crossover on the sine-weighted moving average (SWMA).

- **Weights:** w_i = sin(π·(i+1)/(n+1)) over the last n closes
  (i=0 oldest, i=n−1 most recent), SWMA = Σ(w_i·close_i)/Σ(w_i)
- **Fast:** SWMA(close, 20); **Slow:** SWMA(close, 40)
- **Long:** fast crosses above slow
- **Short:** fast crosses below slow
- **Exit:** the opposite cross
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max hold
  (slow crossover — give legs room), 1% risk/trade, 3x leverage

Parameters: fast=20, slow=40, ATR(14) for stop/trail. WARMUP=60
(slow SWMA(40) spin-up, 40 bars, + margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.sine_weighted_ma_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # 20/40 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the 10/20 – 20/40 – 30/60 sensitivity check.

## Attribution correction

The build brief attributed the SWMA to John Ehlers. The SWMA was
introduced by **Patrick Lafferty** in a 1999 Technical Analysis of
Stocks and Commodities article; Ehlers discusses sine-weighted
averages in "Cybernetic Analysis for Stocks and Futures" / "Rocket
Science for Traders", but he did not originate the indicator. The
formula implemented here is the standard half-sine kernel
sin(π·(i+1)/(n+1)) exactly as specified in the brief, and the
registry source is corrected to Lafferty.

Source: Sine-Weighted Moving Average (Patrick Lafferty, 1999) —
https://www.luxalgo.com/library/concept/sine-weighted-ma/

## Honest caveats

- The half-sine kernel is symmetric and center-weighted, so lag is
  ~half the window (~20 bars on the slow leg) — crosses arrive late,
  after much of a leg has already run. That is the design, not a bug,
  and it is why the 2xATR stop gets hit so often (132–142 of ~160
  trades per coin exit on the stop, only 27 on the signal).
- BTC is a clear loser in the batch window; the combined green is
  ETH + HYPE only, and the combined +$700 on 488 trades is noise-level
  (expectancy +$1.43/trade vs ~$8/trade in fees per trade).
- Single 7-month crypto window; no out-of-sample evidence.
