# LazyBear Squeeze Momentum

The TradingView strategy "Squeeze Momentum Indicator Strategy
[LazyBear + PineIndicators]", built on LazyBear's Squeeze
Momentum indicator — itself a modification of John Carter's TTM
Squeeze (Mastering the Trade, Ch. 11).

## Mechanism

**Squeeze:** Bollinger Bands (20, 2σ, SMA mid) sit strictly
inside Keltner Channels (20 EMA mid, 1.5×ATR(14)) — low
volatility. **Release:** the first bar the bands move back
outside the channels after being inside.

**Momentum:** a linear-regression value, not a plain oscillator.
Let x = close − the average of (a) the midpoint of the
trailing-20-bar high and low and (b) the 20-bar SMA of close.
The momentum value is the fitted value at the current bar of
the 20-bar linear regression of x.

**LONG entry** on release, all on the same bar:

- momentum rising AND positive,
- momentum at its trailing-100-bar low,
- close above EMA(100) and above the prior bar's close.

**SHORT entry** is the mirror: release, momentum falling and
negative, momentum at its trailing-100-bar high, close below
EMA(100) and below the prior close.

## Exits

- Long exits on the first bar momentum starts falling (first
  downtick of the histogram); short exits on the first uptick.
- A 2xATR(14) hard stop is added as a backstop (the source
  recommends a stop-loss but specifies none).

## How this differs from the existing squeeze strategies

`ttm_squeeze` and `bollinger_keltner_squeeze` already implement
the BB-inside-KC squeeze with a regression momentum. This
strategy is distinct in three ways: the entry requires the
momentum value to sit at a trailing-100-bar extreme, it adds
the EMA(100) trend filter and the prior-close confirmation,
and the exit is the first momentum downtick/up-tick rather than
a momentum-direction or opposite-signal exit. Expect correlated
results with the existing squeezes — the squeeze/release core
is shared — but the 100-bar-extreme gate makes entries much
rarer and more selective.

## Risk

2xATR(14) stop, no trail, no target, 120-bar (~5-day) max
hold, 1% risk per trade, 3x leverage cap. WARMUP = 110 bars.

Source: TradingView — Squeeze Momentum Indicator Strategy
[LazyBear + PineIndicators]
(https://th.tradingview.com/script/G40dtEbK-Squeeze-Momentum-Indicator-Strategy-LazyBear-PineIndicators/).
