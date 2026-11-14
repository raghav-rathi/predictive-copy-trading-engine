# GoNoGo Trend

Trend-state entries on Alex Cole's GoNoGo Trend (GoNoGo Charts).

**Reconstruction, not the vendor indicator.** The exact GoNoGo
formula is proprietary and unpublished. This engine rebuilds the
*published checklist* GoNoGo describes — EMA alignment, MACD,
ADX/+DI/−DI, Donchian position, RSI vs 50 — into a −5..+5 composite
score and a zero-line oscillator. It reproduces the structure (Go /
neutral "go fish" / NoGo states, oscillator confirmation), not the
commercial indicator's exact bars. Do not present backtest results
as evidence about the vendor product.

- **Score** (one point per component, +1 bullish / −1 bearish / 0
  neutral):
  - EMA alignment: +1 if EMA9 > EMA21 > EMA50, −1 if reversed
  - MACD(12,26,9) histogram sign: +1 if > 0, −1 if < 0
  - ADX(14) > 20 with +DI > −DI: +1; ADX > 20 with −DI > +DI: −1;
    ADX ≤ 20: 0 (no trend, no point either way)
  - Donchian(50) position: +1 if close in the upper third of the
    range, −1 if in the lower third
  - RSI(14) vs 50: +1 if > 50, −1 if < 50
- **States:** score ≥ +4 strong Go, +2/+3 weak Go, −1..+1 neutral
  (amber, GoNoGo's "go fish"), −2/−3 weak NoGo, ≤ −4 strong NoGo
- **Oscillator:** clip(z50(MACD hist) + (RSI − 50)/25, −6, +6),
  where z50 is the histogram divided by its rolling-50 stddev
- **Long:** state transitions into Go (from neutral/NoGo) with
  oscillator > 0
- **Short:** state transitions into NoGo (from neutral/Go) with
  oscillator < 0
- **Exit:** state falls back to neutral or the opposite state (a
  weak Go still holds a long; only amber or a NoGo flip closes it)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 150-bar max
  hold (never binds on the backtest window — see CALIBRATION.md),
  1% risk/trade, 3x leverage

Parameters: EMA 9/21/50, MACD 12/26/9, ADX 14 (> 20), Donchian 50,
RSI 14, oscillator z-window 50, clamp ±6. WARMUP=80.

Usage:

```python
from strategies.data import fetch_candles
from strategies.gonogo_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for parameter notes and the max-hold sweep.

Sources: GoNoGo Oscillator —
https://www.gonogocharts.com/indicator/gonogo-oscillator/ ;
GoNoGo Trend (Optuma KB) —
https://www.optuma.com/kb/tools/gonogo/gonogo-trend/

## Honest caveats

- This is a checklist reconstruction; the vendor's weighting,
  smoothing, and exact state thresholds are unknown, so the score
  components are equally weighted by construction, not by evidence.
- On 1h crypto the composite flips state often: ~150–190 entries
  per side per coin over 7 months, and the backtest is a loser on
  two of three coins (see BACKTEST.md). The state-transition entry
  is late by design — it waits for all five legs to agree — and on
  1h bars that agreement often arrives at the end of the move.
- The oscillator confirmation (osc > 0 for longs) barely filters
  anything in practice: the oscillator and the score share MACD and
  RSI inputs, so they agree most of the time.
