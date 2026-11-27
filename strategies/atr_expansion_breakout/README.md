# ATR Expansion Breakout (NR7)

Toby Crabel's narrow-range idea: volatility contracts, then
expands. The narrowest-range bar of the last 7 (NR7) marks
the contraction; a close breaking out of that bar's high/low
within the next few bars is the expansion trade.

- **NR7:** range[i] strictly less than each of range[i-6..i-1]
  (narrowest range of the last 7 bars including the current one)
- **Bracket:** the NR7 bar's high/low arm a bracket valid for
  the next 3 bars (j+1..j+3). A newer NR7 re-arms the bracket
  (replaces the old levels, restarts the 3-bar clock).
- **Long:** close crosses ABOVE the armed NR7 high within validity
- **Short:** close crosses BELOW the armed NR7 low within validity
- **Both triggers same bar:** enter NEITHER -- with OHLC data
  the intrabar order is unknowable. (With high >= low a single
  close cannot in practice cross both levels of one bracket,
  so this is a guard, not a live path.)
- **Exit:** close back below the NR7 low that armed a long
  (failed breakout), or back above the NR7 high that armed a
  short; or the opposite entry fires. 2xATR hard stop, 3xATR
  trail, 48-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 48-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: NR window 7 bars, bracket validity 3 bars,
ATR(14) for risk. Entries are CROSS-based
(crossed_above / crossed_below on the armed bracket levels),
never level conditions -- a level condition would re-fire
every bar the close sat beyond the bracket.

Deviations / implementation notes (all documented, none
tuned to PnL):

- The sources describe trading the breakout of the NR7 bar
  "within the next few bars" without fixing a number; 3 bars
  is the shipped reading, and CALIBRATION.md sweeps 2 and 5
  (all three lose; the choice is not what decides outcomes).
- The armed bracket columns are set on the NR7 bar itself as
  well as the 3 following bars (needed so the cross test has
  a previous-bar level to compare against). A close can never
  cross above its own bar's high, so this adds no entries.
- A newer NR7 re-arms the bracket even mid-validity, per the
  brief; the old bracket's pending breakout is abandoned.

Sources: Toby Crabel NR4/NR7 --
https://tradingstrategyguides.com/narrow-range-bars-the-nr4-and-nr7-strategy/
and https://www.loomiai.io/learn/nr7-inside-day-toby-crabel-strategy/

Usage:

```python
from strategies.atr_expansion_breakout import indicators, signals, risk

df = indicators.add_indicators(df)  # nr_n=7, validity_bars=3 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-48 pinned window) results and
CALIBRATION.md for the bracket-validity (2/3/5) and NR-window
(4/7) sensitivity checks.
