# VWMA Crossover

Volume Weighted Moving Average crossover: VWMA(10) vs VWMA(50), where VWMA(n) = sum(close * volume) / sum(volume) over n bars. Volume-weighting makes the average track where the most trading actually happened, so a fast/slow cross reacts to volume-backed moves rather than thin prints.

## Rules

- Long: VWMA(10) crosses above VWMA(50).
- Short: VWMA(10) crosses below VWMA(50).
- Exit: opposite VWMA cross (plus ATR stop / trail).

## Source

- VWMA indicator explained (OneUp Trader): https://blog.oneuptrader.com/analysis/what-is-vwma-indicator-explained/

Paper only, no live execution.
