# Narrow-Range Breakout (NR7)

Toby Crabel's NR7: the setup bar is the bar whose range (high − low) is the smallest of the last 7 bars including itself (ties count). The setup bar's high/low and the trend direction at the setup bar (SMA50 vs SMA200) govern the next 24 bars; a newer setup bar replaces the old one.

## Rules

- Setup: range is the smallest of the last 7 bars. Trend at setup: SMA50 > SMA200 is a long setup, SMA50 < SMA200 a short setup.
- Long: within 24 bars after a long setup, close above the setup bar's high → enter. Exit on a close back below the setup bar's low, or when a new short-trend NR7 setup triggers.
- Short: within 24 bars after a short setup, close below the setup bar's low → enter. Exit on a close back above the setup bar's high, or when a new long-trend NR7 setup triggers.
- Setup levels come from bars strictly before the signal bar, so signals use no future data. ATR stop / trail from the risk layer also applies.

## Source

- Clear Tape — NR7 and Inside Day Breakout Strategy: https://cleartape.ai/strategies/nr7-inside-day-breakout

Paper only, no live execution.
