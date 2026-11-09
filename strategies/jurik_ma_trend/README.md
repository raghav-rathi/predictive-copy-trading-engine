# Jurik MA Trend

Jurik Moving Average (JMA), length 14, phase 50: a low-lag adaptive
moving average by Mark Jurik (Jurik Research, 1999). The original
algorithm was never published, so this uses the widely-circulated
public three-stage reconstruction (see `indicators.py` for the exact
formula):

- beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2); alpha = beta^2
- phase_ratio = clamp(phase / 100 + 1.5, 0.5, 2.5) → 2.0 at phase 50
- Stage 1 (adaptive EMA): e0 = (1-alpha)*price + alpha*e0_prev
- Stage 2 (Kalman detrender): e1 = (price - e0)*(1-beta) + beta*e1_prev; ma2 = e0 + phase_ratio*e1
- Stage 3 (Jurik filter): e2 = (ma2 - JMA_prev)*(1-alpha)^2 + alpha^2*e2_prev; JMA = JMA_prev + e2

State is seeded with e0 = JMA = first close, e1 = e2 = 0.

## Rules

- Long: close crosses above the JMA AND the JMA is rising (above its previous bar). Exit on a cross back below the JMA.
- Short: close crosses below the JMA AND the JMA is falling. Exit on a cross back above the JMA.
- ATR stop / trail from the risk layer also applies.

## Sources

- Wickra docs — JMA (public three-stage reconstruction, formula as implemented): https://docs.wickra.org/Indicators/Indicator-Jma
- Forex-Station — "Jurik JMA Algorithm Revealed — The 3 Stages of Jurik Smoothing" (three-stage form): https://forex-station.com/attach/file/3413178
- TradingView — JurikJMA library by ZurvanEG (Pine reconstruction, Igor Durkin / Nikolay Kositsin lineage): https://in.tradingview.com/script/o7ca42Ht-JurikJMA/

Paper only, no live execution.
