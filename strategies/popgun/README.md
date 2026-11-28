# Popgun Bar Pattern

Jeffrey Kennedy's two-bar Popgun: an inside bar followed by
an outside bar that engulfs it. The outside bar's range is
the "loaded" bracket -- a close breaking out of it is the
trade setup, in the direction of the break.

- **Inside bar:** h[i] < h[i-1] AND l[i] > l[i-1]
- **Outside bar:** h[i] > h[i-1] AND l[i] < l[i-1]
- **Popgun (bar i):** inside[i-1] AND outside[i]
- **Bracket:** the outside bar's high/low arm a bracket valid
  for the next 5 bars (the popgun bar itself included in the
  column for cross-detection). A newer popgun re-arms the
  bracket (replaces the old levels, restarts the 5-bar clock).
- **Long:** close crosses ABOVE the armed popgun high within validity
- **Short:** close crosses BELOW the armed popgun low within validity
- **Both triggers same bar:** enter NEITHER -- with OHLC data
  the intrabar order is unknowable. (With high >= low a single
  close cannot in practice cross both levels of one bracket,
  so this is a guard, not a live path.)
- **Exit:** close back below the popgun low that armed a long
  (failed popgun), or back above the popgun high that armed a
  short; or the opposite entry fires. 2xATR hard stop, 3xATR
  trail, 48-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 48-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: bracket validity 5 bars, ATR(14) for risk.
Entries are CROSS-based (crossed_above / crossed_below on
the armed bracket levels), never level conditions -- a level
condition would re-fire every bar the close sat beyond the
bracket.

Deviations / implementation notes (all documented, none
tuned to PnL):

- Kennedy's write-up leaves the bracket's lifetime open
  ("the next few bars"); 5 bars is the shipped reading,
  and CALIBRATION.md sweeps 3 and 8 (all three lose
  combined; the choice is not what decides outcomes).
- The armed bracket columns are set on the popgun bar itself
  as well as the 5 following bars (needed so the cross test
  has a previous-bar level to compare against). A close can
  never cross above its own bar's high, so this adds no entries.
- A newer popgun re-arms the bracket even mid-validity, per
  the brief; the old bracket's pending breakout is abandoned.

Sources: Popgun bar pattern — Jeffrey Kennedy / Elliott Wave
International --
https://elliottwaveuniversity.com/popgun-twobar-pattern-points-trade-setups/

Usage:

```python
from strategies.popgun import indicators, signals, risk

df = indicators.add_indicators(df)  # validity_bars=5 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-28 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the bracket-validity (3/5/8) sensitivity
check.
