# OBV Cross

Granville's On-Balance Volume turns volume into a trend line: up days add volume, down days subtract it. Crossing OBV against its own EMA(20) trades the volume flow's turn rather than price's — the idea being that smart volume moves first and price follows, so the cross is an early confirmation instead of a lagging price average.

## Mechanism

- OBV = cumulative signed volume (sign of the close-to-close change).
- Signal line = EMA(OBV, 20).
- The cross of the two lines is the entry; the opposite cross exits.

## Entry / exit

- **Long entry:** OBV crosses above EMA(OBV, 20).
- **Short entry:** OBV crosses below EMA(OBV, 20).
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- On-Balance Volume (Joseph Granville):
  https://school.stockcharts.com/doku.php?id=technical_indicators:on_balance_volume

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 34 bars
(20 bars for the OBV EMA + ATR/margin.).

## Honest limitation

On crypto perps, reported volume is venue-specific and wash-prone, so OBV's 'smart money' premise is weaker than on equities — a single large-volume chop bar can flip the cross with no price follow-through. The EMA cross also lags the OBV turn itself, stacking two lags (see BACKTEST.md).

Paper only, no live execution.
