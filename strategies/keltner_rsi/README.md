# Keltner Channel + RSI

## Mechanism

A Keltner channel (EMA(20) midline ± 1.5 × ATR(10)) marks where price has stretched unusually far from its recent trend. A close outside the band is a breakout — but bare channel breakouts fail in two familiar ways: dead chop and vertical blow-offs. The RSI(14) band is the filter: longs require RSI in [50, 75] (momentum confirmed, not yet overbought) and shorts RSI in [25, 50]. The mid-band cross is the exit: once price falls back to trend, the breakout thesis is dead.

## Entry / exit rules

- **Long entry:** close above the Keltner upper band AND RSI(14) in [50, 75].
- **Short entry:** close below the Keltner lower band AND RSI(14) in [25, 50].
- **Long exit:** close crosses back below the Keltner mid-band.
- **Short exit:** close crosses back above the Keltner mid-band.

Entries are level conditions (any qualifying bar can enter); the backtest holds one position at a time, so repeats while in a position are inert. Signals execute at the next bar's open.

## Risk

2xATR stop, 2.5xATR chandelier trail, no fixed target, 168-bar (7-day) max hold, 1% risk/trade, 3x leverage cap.

## Source

Keltner channels (Chester Keltner; Linda Raschke) + RSI (J. Welles Wilder) — https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/keltner-channels

## Honest caveats

- The RSI band does not save the breakout: all three legs lose, including HYPE (−$529), the only coin that carried other batch strategies.
- Breakout entries systematically buy strength that mean-reverts on 1h crypto: win rates 30–34% with profit factors 0.72–0.95.
- Entry signals are level conditions, so the strategy re-enters immediately on the next qualifying bar after an exit — in a grinding trend against the position this stacks losing re-entries.
- Single 7-month crypto window; funding unmodeled; next-bar-open execution vs idealized entry.
