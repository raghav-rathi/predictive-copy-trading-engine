# RSI MA Cross

Trade Wilder's RSI against its own moving average — the
momentum-cross setup, not an overbought/oversold fade. RSI(14)
is computed with Wilder's smoothing (shared via
`strategies.base.rsi`, so every RSI strategy in the library
computes the identical series), and the signal line is a plain
14-bar SMA of the RSI itself.

- **RSI** = 100 − 100 / (1 + RS), RS = Wilder average gain /
  Wilder average loss over 14 bars.
- **Signal line** = SMA(RSI, 14).

## Entries (the cross is the whole thesis)

- **Long:** RSI crosses *above* its SMA(14) — upside momentum is
  accelerating relative to its recent norm.
- **Short:** RSI crosses *below* its SMA(14) — downside momentum
  is accelerating.

Deliberately no level filter (no 30/70 gate): adding one would
turn this into a different strategy (an overbought/oversold
system). In chop the RSI whipsaws across its average, which is
the known cost of the setup; the ATR stop/trail and 72-bar max
hold are the only defences, by design.

## Exits

Pure opposite crosses:

- **long_exit:** RSI crosses below its SMA(14)
- **short_exit:** RSI crosses above its SMA(14)

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (the
opposite cross is the exit), 72-bar (~3-day) max hold, 1% risk
per trade, 3x leverage cap, long/short symmetric.

Parameters: RSI 14, signal SMA 14, ATR 14. All fixed a priori;
no optimization. WARMUP=40.

Usage:

```python
from strategies.rsi_ma_cross import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Relative Strength Index (Wilder, StockCharts) —
  https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index
