# VHF Trend Regime

Adam White's VHF (1991) measures whether price is going anywhere at all: net range travelled divided by total distance travelled over 28 bars. Near 1 the market marched in one direction; near 0 it churned in place. Since VHF has no direction, this system pairs the regime trigger (VHF crossing 0.45) with the oldest direction filter there is — price versus its 28-bar average — and exits when the regime dies (VHF under 0.35).

## Mechanism

- VHF(28) = (highest high - lowest low) / sum |close changes| over 28 bars.
- Regime on: VHF crosses above 0.45 (trending zone per the literature's 0.4+ guideline).
- Regime off: VHF below 0.35 (ranging zone).
- Direction: close vs SMA(28).

## Entry / exit

- **Long entry:** VHF crosses above 0.45 with close above SMA(28).
- **Short entry:** VHF crosses above 0.45 with close below SMA(28).
- **Exit:** VHF falls below 0.35. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Vertical Horizontal Filter (Adam White, Futures 1991):
  https://www.incrediblecharts.com/indicators/vertical_horizontal_filter.php

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 42 bars
(28 bars for VHF + ATR/margin.).

## Honest limitation

VHF is a lagging regime meter: by the time 28 bars confirm a trend, much of it is gone, and the 0.35 exit fires only after the chop has already eaten the gains. Entries also only occur on the exact crossing bar, so a trend that starts before VHF crosses 0.45 is missed entirely (see BACKTEST.md).

Paper only, no live execution.
