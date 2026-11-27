# Alligator + Awesome Oscillator Combo

Bill Williams' Profitunity system from *Trading Chaos*:
trade in the direction of the Alligator's open mouth, enter
on a fractal breakout, and let the Awesome Oscillator
confirm momentum.

- **Alligator:** Wilder-smoothed moving averages (SMMA) of
  the median price (H+L)/2 -- Jaw 13, Teeth 8, Lips 5.
  SMMA[i] = (SMMA[i-1]*(n-1) + price[i]) / n, seeded with
  the simple average of the first n prices.
- **Awesome Oscillator:** AO = SMA(median, 5) -
  SMA(median, 34). AO is "green" when it rises bar over
  bar, "red" when it falls.
- **Fractals:** an up-fractal is a bar whose high is the
  strict maximum of the 5 bars centred on it; a
  down-fractal mirrors on the lows. A fractal is only
  confirmed once the 2 bars after it close, so it enters
  the signal set with a 2-bar lag (causal).
- **Long:** a confirmed up-fractal whose high is above the
  Alligator teeth, and the close CROSSES ABOVE that
  fractal high, with AO > 0 and rising and the mouth open
  upward (lips > teeth > jaw)
- **Short:** mirror -- confirmed down-fractal below the
  teeth, close crosses below its low, AO < 0 and falling,
  lips < teeth < jaw
- **Exit:** close back below the lips (long) / above the
  lips (short), or AO red (green) for 2 consecutive bars,
  or the opposite entry
- **Risk:** 2xATR hard stop, 3xATR chandelier trail,
  120-bar max hold, 1% risk/trade, 3x leverage

Parameters: Jaw 13 / Teeth 8 / Lips 5, AO 5/34, fractal
window 2 bars. The entry cross is judged against the most
recent confirmed fractal level (forward-filled). One
implementation guard, documented: the cross only counts
while the fractal level is unchanged from the previous bar
-- a newly confirmed fractal moves the forward-filled
level, and a cross judged against a level that just jumped
would be a bookkeeping artifact, not a price breakout.

Deviation from the canonical source, documented: the book
displaces the Alligator lines 8/5/3 bars into the future
for plotting. Those shifted values are NOT used here --
the SMMA values are unshifted. Using the forward
displacement in a live signal would be lookahead (it needs
future bars); the displacement is a charting convention,
not a trading rule.

Sources: Bill Williams Profitunity / Trading Chaos --
https://www.mql5.com/en/articles/16365

Usage:

```python
from strategies.alligator_awesome_combo import indicators, signals, risk

df = indicators.add_indicators(df)  # frac_n=2 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-48 pinned window) results and
CALIBRATION.md for the fractal-window 1/2/3 sensitivity check.
