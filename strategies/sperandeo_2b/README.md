# Sperandeo 2B False-Breakout Reversal

Victor Sperandeo's 2B pattern from *Trader Vic II: Principles of
Professional Speculation*: a market makes a new 20-bar high, pulls
back, then breaks out above that high — and fails. The failed
breakout traps the breakout buyers, and the reversal back through
the breakout bar's low is the short signal. The bottom version is
the exact mirror.

## Rules

- **2B Top (short):** (1) new 20-bar high; (2) pullback of at least
  3 bars with no new 20-bar high; (3) a breakout bar closes above
  that 20-bar high; (4) a subsequent bar closes below the breakout
  bar's low — that close is the short entry.
- **2B Bottom (long):** mirror image — new 20-bar low, 3+ bar
  pullback, breakout bar closes below the low, then a bar closes
  above the breakout bar's high.
- Only the most recent qualifying 20-bar extreme is tracked; the
  pattern resets once a 2B fires or a newer 20-bar extreme forms.
- Exit on the opposite 2B pattern, plus the risk layer: 2.0x ATR
  stop, 2.5x ATR trail, 10.0x ATR target (5x the stop distance),
  120-bar max hold.
- All computation is causal, so signals on bar i use only data
  through bar i's close.

## Source

- Victor Sperandeo, *Trader Vic II: Principles of Professional
  Speculation*, John Wiley & Sons (1994)
- RoboForex explainer (1-2-3 reversal and 2B pattern):
  https://roboforex.com/blog/education/trading-like-sperandeo-1-2-3-reversal-and-2b-pattern/

Paper only, no live execution.
