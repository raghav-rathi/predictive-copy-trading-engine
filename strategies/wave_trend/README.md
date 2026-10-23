# WaveTrend Oscillator (LazyBear)

The classic open-source crypto reversal oscillator, ported as a
signal engine for 1h Hyperliquid perps.

## Mechanism

LazyBear's WaveTrend normalizes price distance from an EMA by a
second EMA of that distance, producing a bounded oscillation
centered near zero:

- **ap** = (h + l + c) / 3 — typical price
- **esa** = EMA(ap, 10)
- **d** = EMA(|ap − esa|, 10) — average deviation, the scale
- **ci** = (ap − esa) / (0.015 × d) — scaled momentum; the 0.015
  constant is LazyBear's normalization so that the series
  oscillates roughly in ±100. Guarded: ci = 0 when d == 0 (a
  perfectly flat price would otherwise produce 0/0).
- **wt1** = EMA(ci, 21) — the fast oscillator line ("tci" in the
  Pine source)
- **wt2** = SMA(wt1, 4) — the slow signal line

The ±53 lines are LazyBear's oversold/overbought zones; ±60 are
the exhaustion extremes.

## Signals (canonical cross-in-zone rules)

- **Long:** wt1 crosses above wt2 *from the oversold zone* —
  `crossed_above(wt1, wt2)` AND prior-bar wt1 < -53 (the bullish
  reversal out of oversold).
- **Short:** wt1 crosses below wt2 *from the overbought zone* —
  `crossed_below(wt1, wt2)` AND prior-bar wt1 > +53 (the bearish
  reversal out of overbought).
- **Long exit:** wt1 crosses back below wt2, OR wt1 > +60
  (upside exhaustion — the reversal is spent).
- **Short exit:** wt1 crosses back above wt2, OR wt1 < -60.

A cross outside the zones is not an entry — the zone gate is the
whole point of the LazyBear rule. All signal columns are boolean,
NaN-free, no lookahead (bar-i signals use data through bar-i
close).

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (exits
are oscillator-driven), 72-bar (~3-day) max hold, 1% risk/trade,
3x leverage cap. Both directions — the oscillator is symmetric by
construction. WARMUP=80.

Parameters (fixed a priori, canonical LazyBear release — no
optimization): n1=10, n2=21, wt2 SMA 4, zones ±53, extremes ±60.

Usage:

```python
from strategies.wave_trend import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results
(honest loser on all three coins) and CALIBRATION.md for the
no-sweep decision.

Sources:

- LazyBear WaveTrend port + strategy logic —
  https://www.fmz.com/lang/en/strategy/449714
- LazyBear WaveTrend discussion/mechanics —
  https://usethinkscript.com/threads/wavetrend-oscillator-for-thinkorswim-lazybear.233/page-4
