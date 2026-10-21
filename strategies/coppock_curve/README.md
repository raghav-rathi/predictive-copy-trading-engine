# Coppock Curve — zero-cross momentum oscillator

The Coppock curve of E.S.C. Coppock (Barron's, 1962): `WMA(ROC(14) +
ROC(11), 10)` with linear weights, newest bar heaviest. The classic
signal is the curve crossing the zero line (momentum turning from
negative to positive = buy), mirrored here for shorts with the
opposite cross as the exit.

**Honest mechanics note:** Coppock built this for MONTHLY index
closes — the 14- and 11-month lookbacks were the 11-to-14-month
"mourning period" he had read about in church pastoral work. Running
the same (14, 11, 10) on 1h crypto closes turns it into a fast
momentum oscillator, not a bottom-detector. The canonical params ship
as specified anyway, for comparability; the mismatch is documented
under Limitations in BACKTEST.md.

## Usage

```python
import strategies.coppock_curve as S  # registers SPEC

df = S.indicators.add_indicators(raw_ohlcv)   # adds roc14, roc11, coppock, atr
sig = S.signals.add_signals(df)              # adds long_entry/short_entry/long_exit/short_exit
```

## Signals

- `long_entry`: Coppock crosses **above** zero
- `short_entry`: Coppock crosses **below** zero
- `long_exit` / `short_exit`: the opposite cross

No breakout filter, no signal-line filter — the raw zero-cross is the
trade, which keeps entries frequent on a 1h chart.

## Risk

2xATR hard stop, 3xATR chandelier trail, no fixed target (the
opposite cross is the natural exit), 200-bar max hold, 1% risk per
trade on the stop, 3x leverage cap. WARMUP=60 bars (ROC(14) + WMA(10)
spin-up, with margin).
