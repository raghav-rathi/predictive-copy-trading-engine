# Diamond Pattern

## Mechanism

A diamond is a broadening formation followed by a narrowing one:
volatility expands, then contracts, and the break out of the
contracting phase is the trade. This engine detects it causally
— at bar i the pattern is a window ending at bar i-1, and the
breakout bar itself is never part of the pattern:

- **Expanding phase:** bar ranges widen into an apex (the
  widest bar-range in the window), with highs rising and lows
  falling into the apex; apex range > 1.3x the start range.
- **Contracting phase:** bar ranges narrow out of the apex,
  with highs falling and lows rising; end range < 0.7x the apex
  range.
- **Length:** total pattern 15–40 bars, each phase at least 5
  bars.
- **Breakout:** close beyond the converging-phase boundary (max
  high from the apex through bar i-1 for longs, min low for
  shorts) on volume above 1.2x the pattern average.

## Entry / exit rules

- Long entry: upside breakout bar while flat.
- Short entry: downside breakout bar while flat.
- Long exit: a downside breakout bar while long. Short exit
  mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 168-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Classic diamond top/bottom reversal — Edwards & Magee,
*Technical Analysis of Stock Trends*; summary at
https://www.investopedia.com/terms/d/diamondtop.asp

## Honest caveats

- The backtest (see BACKTEST.md) is a small net loser overall,
  with a split book: ETH wins (+$934, PF 1.57) while HYPE loses
  badly (-$1,161, PF 0.25). A pattern that works on one coin and
  collapses on another is not a finding, it is variance.
- Diamonds are rare (97 trades in 7 months across three coins)
  and the detection is the loosest in this batch: "expanding then
  contracting ranges" is a shape many random windows
  approximate, and the volume filter does most of the real
  filtering.
- Almost every trade exits on the stop (95 of 97); the opposite-
  breakout exit is nearly theoretical.
- Paper/backtest only. Nothing here touches live execution.
