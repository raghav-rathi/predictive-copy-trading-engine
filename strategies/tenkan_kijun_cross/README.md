# Ichimoku Tenkan/Kijun Cross

The classic Ichimoku momentum signal, traded bare: Tenkan-sen(9)
crossing Kijun-sen(26).

- Tenkan-sen = (highest high + lowest low over 9 bars) / 2.
- Kijun-sen = (highest high + lowest low over 26 bars) / 2.

## Rules

- Long: Tenkan-sen crosses above Kijun-sen. Exit on Tenkan crossing below Kijun.
- Short: Tenkan-sen crosses below Kijun-sen. Exit on Tenkan crossing above Kijun.
- No cloud, price, or Chikou filter — the cross alone, exactly as briefed.
- All lines are causal rolling midpoints, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Distinction from `kijun_cross`

The existing `strategies/kijun_cross/` trades the **close crossing
the Kijun-sen** (price vs baseline). This strategy trades the two
Ichimoku lines crossing **each other** (Tenkan-sen vs Kijun-sen).
Different trigger, different trade set — a close can cross Kijun
while Tenkan stays above/below it, and vice versa. The test suite
includes a case proving the two disagree on the same frame.

## Source

- BabyPips — Ichimoku Kinko Hyo: https://www.babypips.com/learn/forex/ichimoku-kinko-hyo

Paper only, no live execution.
