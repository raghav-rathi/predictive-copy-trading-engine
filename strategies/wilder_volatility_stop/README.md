# Wilder Volatility Stop

Welles Wilder's Volatility Stop (*New Concepts in Technical Trading Systems*, 1978): a trailing stop placed 3×ATR(7) behind the significant close (SIC — the highest close reached while trending up, the lowest close while trending down). A close through the stop flips the trend and enters the other side.

## Rules

- Trend +1 (up) / −1 (down); SIC = highest close while up / lowest close while down; stop = SIC − 3×ATR(7) while up, SIC + 3×ATR(7) while down.
- Initial trend at warmup: +1 if close > SMA(20), else −1; SIC = close at that bar.
- Long: close above the stop while trending down (flip to up).
- Short: close below the stop while trending up (flip to down).
- Exit: the opposite flip (plus ATR stop / trail).

## Source

- Welles Wilder, *New Concepts in Technical Trading Systems* (1978): https://www.incrediblecharts.com/indicators/volatility_stops.php

Paper only, no live execution.
