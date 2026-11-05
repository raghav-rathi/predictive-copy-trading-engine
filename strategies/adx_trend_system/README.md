# ADX Trend System

ADX trend system (J. Welles Wilder, "New Concepts in Technical Trading Systems", 1978). ADX measures trend strength without direction; +DI / -DI give the direction. The system only trades DI crosses when the trend is already strong (ADX > 25), and steps aside when trend strength fades (ADX < 20).

## Rules

- Long: +DI crosses above -DI and ADX > 25.
- Short: -DI crosses above +DI and ADX > 25.
- Exit: opposite DI cross or ADX falling below 20 (plus ATR stop / trail).

## Source

- ADX indicator (Kagels Trading): https://kagels-trading.com/blog/adx-indicator/

Paper only, no live execution.
