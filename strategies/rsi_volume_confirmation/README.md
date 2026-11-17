# RSI Volume Confirmation

RSI(14) momentum crosses confirmed by volume: a move through the
RSI 50 midline only counts when the crowd is actually trading —
volume above 1.25x its trailing 20-bar mean on the cross bar.

## Rules

- **Long entry:** RSI crosses above 50 AND volume > 1.25x the
  trailing 20-bar mean volume (previous 20 bars, shifted by 1).
- **Short entry:** RSI crosses below 50 AND volume > 1.25x the
  trailing 20-bar mean volume.
- **Long exit:** RSI crosses below 50.
- **Short exit:** RSI crosses above 50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

RSI uses Wilder smoothing (`strategies/base.py: rsi`). The volume
mean excludes the current bar so a spike bar does not dilute its
own comparison. All computation is causal, so signals on bar i use
only data through bar i's close.

## Source

- RSI(14) + volume confirmation, per the batch-38 spec (RSI 50
  midline cross with a 1.25x trailing-20-bar volume filter).

Paper only, no live execution.
