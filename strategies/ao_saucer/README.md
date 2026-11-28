# AO Saucer (Bill Williams)

Bill Williams' Awesome Oscillator Saucer from *New Trading
Dimensions*: AO turns from red (falling) to green (rising)
above zero -- a momentum trough that, per Williams, is the
buy setup -- and the mirror below zero is the sell setup.

- **AO:** SMA(median, 5) − SMA(median, 34), median = (h + l) / 2
- **Buy saucer (bar i):** ao[i] > 0, ao[i-1] > 0, ao[i-2] > 0,
  ao[i-1] < ao[i-2] (red: AO falling) and ao[i] > ao[i-1]
  (green: AO rising again). The saucer completes on bar i.
- **Sell saucer:** mirror -- all three AO bars below zero,
  ao[i-1] > ao[i-2] (green) and ao[i] < ao[i-1] (red).
- **Exit:** long exits on crossed_below(ao, 0) OR a sell
  saucer; short exits on crossed_above(ao, 0) OR a buy
  saucer. A saucer that closes one side opens the other.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 96-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: AO fast 5 / slow 34 (Williams' standard),
ATR(14) for risk. Entries are discrete pattern completions
(a red-to-green AO turn on a single bar), never level
conditions -- a saucer fires once and cannot re-fire while
AO keeps rising.

Deviations / implementation notes (all documented, none
tuned to PnL):

- Williams' original saucer also admits a "twin peaks"
  variant and, in some readings, trades the saucer only
  after a confirming bar; the shipped rule trades the
  completion bar itself (executed at next-bar open by the
  harness), per the brief.
- The zero-cross exit is the shipped rule; the two-bar
  adverse-AO exit is swept in CALIBRATION.md only.
- The "relaxed" saucer (only ao[i], ao[i-1] required above
  zero) is provably identical to the strict rule: ao[i-1] > 0
  plus the turn ao[i-1] < ao[i-2] forces ao[i-2] > 0, so the
  dropped condition never binds. See CALIBRATION.md.

Sources: Awesome Oscillator Saucer — Bill Williams,
*New Trading Dimensions* --
https://www.mql5.com/en/code/13

Usage:

```python
from strategies.ao_saucer import indicators, signals, risk

df = indicators.add_indicators(df)  # AO(5, 34) default
sig = signals.add_signals(df)  # strict=True, exit_mode="zero" default
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-28 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the strict/relaxed and exit-rule
sensitivity checks.
