# Kaufman's Adaptive Moving Average

Kaufman's Adaptive Moving Average KAMA(10,2,30) (Perry Kaufman, "Smarter Trading", 1995): the smoothing constant adapts to market efficiency — fast when price trends cleanly, slow when it chops. ER = |close - close 10 ago| / sum(|close - prior close|) over 10 bars; SC = [ER * (2/3 - 2/31) + 2/31]^2; KAMA = prev KAMA + SC * (close - prev KAMA).

## Rules

- Long: close crosses above KAMA and KAMA is rising.
- Short: close crosses below KAMA and KAMA is falling.
- Exit: opposite cross.
- Plus ATR stop / trail from the batch-standard risk layer.

## Source

- Kaufman's Adaptive Moving Average (KAMA): https://corporatefinanceinstitute.com/resources/capital_markets/kaufmans-adaptive-moving-average-kama/

Paper only, no live execution.
