# Support Resistance Flip

Break-and-retest / role-reversal: a level that has been tested,
breaks, and is then retested from the other side and holds has
flipped role — old resistance becomes support, old support
becomes resistance. The entry is on the retest, not the break.

## Rules

- **Levels:** 5-bar pivot swing highs/lows (a swing high is a
  high strictly greater than the 2 bars on each side; swing low
  mirror) with pivot centre inside the trailing 50-bar window.
  A pivot is recorded at its confirmation bar (centre + 2).
- **A level counts only if price touched it at least twice:**
  bars in the trailing 50-bar window whose low is within 0.5x
  ATR(14) of the level.
- **Break:** a close crosses beyond the level (above a
  resistance level, below a support level). The break opens a
  pending setup; it is not an entry.
- **Retest (long entry):** within the next 20 bars after the
  break, a bar whose low comes within 0.5x ATR of the broken
  resistance level AND whose close is back above the level
  (bullish hold). Entry fires on that retest-hold bar.
- **Retest (short entry):** mirror image for a broken support
  level (low within 0.5x ATR, close back below the level).
- **Exit long:** close back below the flipped level.
  **Exit short:** close back above the flipped level.
- If no retest within 20 bars the setup expires with no trade.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 120 bars.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Sources

- Break-and-retest strategy, Prometheus Markets:
  https://www.prometheus-markets.com/analysis-education/break-and-retest-strategy-trading-breakouts-with-confirmation/
- What is retest, HowToTrade:
  https://howtotrade.blog/what-is-retest/

Paper only, no live execution.
