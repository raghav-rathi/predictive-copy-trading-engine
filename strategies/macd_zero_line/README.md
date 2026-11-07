# MACD Zero-Line Cross

MACD(12, 26, 9) zero-line cross system: the MACD line is EMA(12) minus EMA(26) of close; long when the line crosses above zero, short when it crosses below zero, exit on the reverse zero cross. A pure momentum regime flip — the fast EMA overtaking the slow EMA.

## Rules

- Long: MACD line crosses above zero (previous bar ≤ 0, current bar > 0).
- Short: MACD line crosses below zero (previous bar ≥ 0, current bar < 0).
- Exit: reverse zero cross, plus ATR stop / trail from the batch-standard risk layer.
- Signals use only data through the current bar's close — no lookahead.

## Source

- MACD indicator strategy (qtfx.dev): https://www.qtfx.dev/en/indicators/macd-indicator-strategy/

Paper only, no live execution.
