# Wyckoff Distribution

The Wyckoff distribution schematic, short only: after an
advance, a buying climax and an upthrust after distribution
(UTAD, a false breakout) mark the end of markup; a sign of
weakness confirms supply, and a last point of supply is the
low-risk entry.

This is the bearish mirror of `strategies/wyckoff_accumulation`
(batch 48). The machinery is identical with every sign
flipped: decline gate -> advance gate, spring -> UTAD, SOS ->
SOW, LPS -> LPSY, long -> short, range projection upward ->
range projection downward. Read the accumulation module
first; the notes below only record where the mirror differs.

- **Range:** trailing 120-bar high/low (range_high_120 /
  range_low_120); midpoint = low + 50% of the range
- **Advance gate:** close 120 bars ago <= 95% of the current
  close -- the schematic only exists after an advance of
  >= 5% over 120 bars; gates the UTAD
- **Buying climax (BC):** bar range > 2x ATR(14) AND close in
  the upper 25% of its own range AND volume > 1.5x vol-SMA(20).
  Recorded as a diagnostic anchor; the entry chain does not
  require it (the range edges are the trailing 120-bar
  high/low regardless)
- **UTAD:** the high pokes above the trailing 120-bar high and
  the close reclaims back below that level within 3 bars
  (same-bar reclaim allowed). utad_high = highest high of the
  poke. A higher high while waiting re-anchors the poke (new
  3-bar clock, higher utad_high).
- **SOW (sign of weakness):** after a UTAD (within the last
  48 bars), a wide down bar: close below the range midpoint AND
  bar range > 1.5x ATR AND volume > 1.2x vol-SMA(20). First
  such bar per UTAD only.
- **LPSY (last point of supply):** after an SOW (within 24
  bars), the first bar whose high holds below utad_high and
  whose close is below range_high (a lower-high pullback)
- **Short entry:** on the UTAD-reclaim bar's close, OR on an
  LPSY bar after an SOW. SHORT ONLY: allow_longs=False --
  distribution is a bearish schematic; the mirror
  accumulation setup is a different strategy.
- **Exit:** close above utad_high (invalidation -- the UTAD
  failed) OR close below the cause-effect range projection
  range_low - 1.0x (range_high - range_low). 2xATR hard stop,
  3xATR trail, 120-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: range 120 bars, advance 5% over 120 bars, ATR(14),
vol-SMA(20), UTAD reclaim 3 bars, SOW window 48 bars, LPSY
window 24 bars, projection 1.0x range. UTAD, SOW, and LPSY
are single-fire state-machine events (each fires on exactly
one bar per setup), not persistent level conditions, so an
entry cannot re-fire while a level condition persists.

Deviations / implementation notes (all documented, none
tuned to PnL):

- The poke is measured against the trailing range high BEFORE
  the poke bar (the current bar's high is part of the rolling
  120-bar window, so high > range_high could never be true
  otherwise). The poke level is frozen at the poke bar and the
  reclaim is judged against that frozen level. This is the
  exact mirror of the accumulation spring's "measured against
  the range low before the dip bar" guard.
- The buying climax is recorded but does not gate the
  entry chain: the range edges are the trailing 120-bar
  high/low regardless, so the climax is a diagnostic, not a
  filter -- the mirror of the accumulation selling climax.
- Exit levels are frozen at the entry bar (utad_high of the
  UTAD that produced the entry; projection from the range
  at the entry bar). A live trailing range would move the
  invalidation while the trade is open.
- SOW and LPSY are first-bar-only per UTAD/SOW: after an SOW
  fires, the next qualifying pullback bar is the LPSY; later
  qualifying bars do not re-fire. Without this, any bar
  holding below utad_high after an SOW would be an LPSY and
  entries would re-fire for days.
- The schematic's Phase A-E labels and the "test of the
  UTAD" are not separately modeled; the UTAD + SOW + LPSY
  chain is the tradeable core on 1h bars.
- Max hold is 120 bars (not the accumulation's 240): a
  distribution top resolves faster than an accumulation
  base on this tape, and the brief fixes 120.

Source: Wyckoff distribution schematic — Wyckoff method --
https://www.cmcmarkets.com/en-gb/trading-strategy/what-is-wyckoff-method

Usage:

```python
from strategies.wyckoff_distribution import indicators, signals, risk

df = indicators.add_indicators(df)  # range_n=120 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-28 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the UTAD-reclaim (3/5) and range-window
(120/240) sensitivity checks.
