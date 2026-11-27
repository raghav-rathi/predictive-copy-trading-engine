# Wyckoff Accumulation

The Wyckoff accumulation schematic, long only: after a
decline, a selling climax and a spring (false breakdown)
mark the end of markdown; a sign of strength confirms
demand, and a last point of support is the low-risk entry.

- **Range:** trailing 120-bar high/low (range_high_120 /
  range_low_120); midpoint = low + 50% of the range
- **Decline gate:** close 120 bars ago >= 5% above the
  current close -- the schematic only exists after a decline;
  gates the spring
- **Selling climax:** bar range > 2x ATR(14) AND close in
  the lower 25% of its own range AND volume > 1.5x vol-SMA(20).
  Recorded as a diagnostic anchor; the entry chain does not
  require it (the range edges are the trailing 120-bar
  high/low regardless)
- **Spring:** the low dips below the trailing 120-bar low and
  the close reclaims back above that level within 3 bars
  (same-bar reclaim allowed). spring_low = lowest low of the
  dip. A lower low while waiting re-anchors the dip (new
  3-bar clock, deeper spring_low).
- **SOS (sign of strength):** after a spring (within the last
  48 bars), a wide up bar: close above the range midpoint AND
  bar range > 1.5x ATR AND volume > 1.2x vol-SMA(20). First
  such bar per spring only.
- **LPS (last point of support):** after an SOS (within 24
  bars), the first bar whose low holds above spring_low and
  whose close is above range_low (a higher-low pullback)
- **Long entry:** on the spring-reclaim bar's close, OR on an
  LPS bar after an SOS. LONG ONLY: allow_shorts=False --
  accumulation is a bullish schematic; the mirror
  distribution setup is a different strategy.
- **Exit:** close below spring_low (invalidation -- the spring
  failed) OR close above the cause-effect range projection
  range_high + 1.0x (range_high - range_low). 2xATR hard stop,
  3xATR trail, 240-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 240-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: range 120 bars, decline 5% over 120 bars, ATR(14),
vol-SMA(20), spring reclaim 3 bars, SOS window 48 bars, LPS
window 24 bars, projection 1.0x range. Spring, SOS, and LPS
are single-fire state-machine events (each fires on exactly
one bar per setup), not persistent level conditions, so an
entry cannot re-fire while a level condition persists.

Deviations / implementation notes (all documented, none
tuned to PnL):

- The dip is measured against the trailing range low BEFORE
  the dip bar (the current bar's low is part of the rolling
  120-bar window, so low < range_low could never be true
  otherwise). The dip level is frozen at the dip bar and the
  reclaim is judged against that frozen level.
- The selling climax is recorded but does not gate the
  entry chain: the brief says to record it and that the range
  edges are the trailing 120-bar high/low regardless, so the
  climax is a diagnostic, not a filter.
- Exit levels are frozen at the entry bar (spring_low of the
  spring that produced the entry; projection from the range
  at the entry bar). A live trailing range would move the
  invalidation while the trade is open.
- SOS and LPS are first-bar-only per spring/SOS: after an SOS
  fires, the next qualifying pullback bar is the LPS; later
  qualifying bars do not re-fire. Without this, any bar
  holding above spring_low after an SOS would be an LPS and
  entries would re-fire for days.
- The schematic's Phase A-E labels and the "test of the
  spring" are not separately modeled; the spring + SOS + LPS
  chain is the tradeable core on 1h bars.

Source: Wyckoff accumulation --
https://www.chartguys.com/chart-patterns/wyckoff-accumulation

Usage:

```python
from strategies.wyckoff_accumulation import indicators, signals, risk

df = indicators.add_indicators(df)  # range_n=120 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-48 pinned window) results and
CALIBRATION.md for the spring-reclaim (2/3/5) and SOS-window
(24/48/96) sensitivity checks.
