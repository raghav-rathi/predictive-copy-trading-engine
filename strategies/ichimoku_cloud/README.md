# Ichimoku Cloud

Ichimoku (Goichi Hosoda, 9/26/52): long on a Tenkan crossing above the Kijun while the close is above the cloud and the cloud ahead is green, with Chikou confirmation (current close above the close 26 bars ago); short mirror. Exit on a Tenkan/Kijun cross back or a close into the cloud.

## Rules

- Long: Tenkan crosses above Kijun, close above both Senkou spans, cloud ahead green (Senkou A > Senkou B), and current close above the close 26 bars ago (Chikou confirmation).
- Short: Tenkan crosses below Kijun, close below both Senkou spans, cloud ahead red, and current close below the close 26 bars ago.
- Exit: Tenkan/Kijun cross back, or a close into the cloud (plus ATR stop / trail).
- The Chikou check uses only past closes (c vs c 26 bars ago). `B.ichimoku()`'s `chikou` column (c.shift(-26)) contains future closes and is never used.

## Source

- Ichimoku Cloud: https://velotrade.com/blog/ichimoku-cloud

Paper only, no live execution.
