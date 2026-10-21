# Know Sure Thing (KST) — signal-line cross momentum

Martin Pring's Know Sure Thing, a summed momentum oscillator over
four timeframes:

```
KST = 1*SMA(ROC(10),10) + 2*SMA(ROC(15),10)
    + 3*SMA(ROC(20),10) + 4*SMA(ROC(30),15)
signal = SMA(KST, 9)
```

The longest timeframe carries the largest weight (4x), so KST turns
later than a single ROC but stays smooth. The 9-bar signal line is
Pring's standard trigger.

## Usage

```python
import strategies.kst as S  # registers SPEC

df = S.indicators.add_indicators(raw_ohlcv)   # adds kst, kst_signal, atr
sig = S.signals.add_signals(df)              # adds long_entry/short_entry/long_exit/short_exit
```

## Signals

- `long_entry`: KST crosses **above** its signal line **while KST is
  still below zero** (early-turn entry, not a late extension)
- `short_entry`: KST crosses **below** its signal line **while KST is
  still above zero**
- `long_exit` / `short_exit`: the opposite cross (ungated)

## Risk

2xATR hard stop, 3xATR chandelier trail, no fixed target (the
opposite cross is the natural exit), 200-bar max hold, 1% risk per
trade on the stop, 3x leverage cap. WARMUP=80 bars (ROC(30) + 15-bar
SMA + 9-bar signal spin-up, with margin).
