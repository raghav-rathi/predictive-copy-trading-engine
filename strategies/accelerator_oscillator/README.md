# Accelerator Oscillator (Bill Williams)

Williams' Acceleration/Deceleration oscillator from *New Trading
Dimensions*: the second derivative of price, i.e. the acceleration of
momentum. The driving force (AO) tells you which way momentum points;
AC tells you whether that force is speeding up or slowing down — and
it changes direction before AO, which changes direction before price.

- **Median price** = (high + low) / 2
- **AO** = SMA(med, 5) − SMA(med, 34)
- **AC** = AO − SMA(AO, 5)
- **Color:** green when AC[j] > AC[j−1] (acceleration rising), red when
  AC[j] < AC[j−1]; a flat bar is neither and breaks a color run. The
  color is the bar-to-bar *change*, not the level — a rising bar below
  the zero line is green, a falling bar above the zero line is red.

## Rules (Williams' 2-vs-3 bar confirmation)

With the driving force (trade agreeing with where the force points):

- **Long:** AC > 0 and the last 2 bars are green
- **Short:** AC < 0 and the last 2 bars are red

Against the driving force (counter-trend, needs stronger confirmation):

- **Long:** AC < 0 and the last 3 bars are green
- **Short:** AC > 0 and the last 3 bars are red

The zero line itself is never a signal — a sign change without the
required consecutive color run is not an entry. Williams' iron rule:
never buy on a red bar, never sell on a green bar.

**Exits:** the opposite entry condition, or 2 consecutive bars of the
color against the position (the acceleration that justified the trade
has reversed).

**Risk:** 2xATR hard stop, 2.5xATR chandelier trail, 120-bar max hold,
1% risk/trade, 3x leverage. No fixed target — AC exits are
color-driven.

Parameters: fast=5, slow=34, signal=5 (Williams' originals, fixed a
priori — see CALIBRATION.md), ATR(14) for stop/trail. WARMUP=50.

Usage:

```python
from strategies.accelerator_oscillator import indicators, signals, risk

ind = indicators.add_indicators(df)          # fast=5, slow=34, signal=5 default
sig = signals.add_signals(ind)
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the slow=21/34/55 sensitivity check.

Sources:

- Accelerator Oscillator vs Awesome Oscillator (gate.com) —
  https://www.gate.com/learn/articles/accelerator-oscillator-vs-awesome-oscillator
- forexsrovnavac.cz AO/AC guide (referenced per batch brief; exact
  article URL not verified — see the gate.com article above for the
  2-vs-3 bar rule statement)
- The 2-bar with-trend / 3-bar counter-trend rule is also documented
  in the Orbex and tradingpedia AC guides:
  https://support.orbex.com/en/articles/528864-trading-indicator-accelerator-decelerator-oscillator
  and https://www.tradingpedia.com/forex-trading-indicators/accelerator-oscillator/
