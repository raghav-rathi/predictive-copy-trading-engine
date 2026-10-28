# ADX + MACD Trend

## Mechanism

Three filters must agree before an entry:

1. **Trend strength** — Wilder ADX(14) > 25. Below that the market is
   range-bound and MACD crosses are noise, so no trade.
2. **Trend direction** — +DI > -DI for longs, -DI > +DI for shorts.
   Entries only ride the prevailing directional move.
3. **Momentum timing** — the MACD line (12, 26, 9) crossing its
   signal line. This is the trigger, not the thesis.

## Entry / exit rules

- **Long entry:** MACD crosses above signal AND ADX > 25 AND +DI > -DI.
- **Short entry:** MACD crosses below signal AND ADX > 25 AND -DI > +DI.
- **Long exit:** MACD crosses below signal, OR ADX crosses below 20
  (trend strength has collapsed).
- **Short exit:** MACD crosses above signal, OR ADX crosses below 20.
- Risk layer: 2xATR hard stop, 2.5xATR chandelier trail, no fixed
  target, 168-bar (~7-day) max hold, 1% equity risk per trade,
  3x leverage cap.

## Source

Wilder DMI/ADX (J. Welles Wilder Jr., *New Concepts in Technical
Trading Systems*) combined with Appel MACD (Gerald Appel) — both
textbook, no proprietary claim.

## Honest caveats

- The ADX > 25 gate does not save MACD crosses at 1h granularity:
  on this window the strategy still loses on all three coins with
  win rates of 26–33% (see BACKTEST.md). The gate cuts trade count
  versus raw MACD, but the surviving crosses are still mostly
  late-to-trend or mid-chop.
- ADX is a lagging smoother: by the time ADX clears 25, much of the
  move that built it is already over, and the MACD cross that
  follows is often the exhaustion leg.
- No parameter was tuned on this window; the thresholds (25 / 20)
  are the textbook Wilder levels, shipped as-is.
