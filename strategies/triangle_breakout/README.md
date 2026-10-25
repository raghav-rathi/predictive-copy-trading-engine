# Triangle Breakout

Ascending and descending triangles only — no symmetrical triangles,
whose breakout direction is a coin flip. Ascending: flat resistance
(two swing highs within 1%) with rising support (each swing low
higher than the last), traded long on a close above resistance.
Descending is the mirror: flat support, falling resistance, traded
short on a close below support.

## Rules

- Ascending pending: two highs within 1%, lows ascending. Long on a
  close above the resistance high.
- Descending pending: two lows within 1%, highs descending. Short on
  a close below the support low.
- Invalidation: ascending clears if price breaks below the rising
  support low; descending clears if price breaks above the falling
  resistance high.
- Exit: close back inside the entry level (failed breakout), or the
  opposite triangle's breakout.
- Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target,
  96-bar (4-day) max hold, 1% equity risk per trade, 3x leverage cap

Source: ascending / descending triangles (Bulkowski, Encyclopedia
of Chart Patterns).
