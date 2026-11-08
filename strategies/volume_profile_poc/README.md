# Volume Profile POC

Rolling 168-bar volume profile. The window's price range (min low → max high) is split into 24 equal bins; each bar's volume is assigned to the bin containing its close. POC is the price level where the most volume traded (volume-weighted mean close of the highest-volume bin — see CALIBRATION.md). VAH/VAL bound the smallest contiguous bin set around the POC bin holding at least 70% of the window's volume.

## Rules

- Bias: close above POC = long bias, below POC = short bias.
- Long: the bar's low dips to within 0.5x ATR(14) of POC (low ≤ POC + 0.5×ATR) and the close comes back above POC, while the prior bar's close was above its POC (a pullback to POC from above, not a cross from below). Exit at close ≥ VAH or close < POC.
- Short: the bar's high reaches to within 0.5x ATR(14) of POC (high ≥ POC − 0.5×ATR) and the close falls back below POC, while the prior bar's close was below its POC. Exit at close ≤ VAL or close > POC.
- All levels use only data through the signal bar's close. ATR stop / trail from the risk layer also applies.

## Source

- PriceActionNinja — POC Trading Strategy: https://priceactionninja.com/poc-trading-strategy/

Paper only, no live execution.
