# True Strength Index — Calibration

All parameters were fixed **a priori** from the canonical published
definition — no in-sample selection, no sweep, no tuning on the
backtest data:

| Parameter | Value | Origin |
|---|---|---|
| Momentum smoothing r | 25 | Blau's canonical TSI(25, 13, 7) |
| Absolute-momentum smoothing s | 13 | Blau's canonical TSI(25, 13, 7) |
| Signal-line EMA | 7 | Blau's canonical TSI(25, 13, 7) |
| Zero-territory filter | TSI > 0 longs / TSI < 0 shorts | design decision, not a tuned threshold |
| Stop | 1.5 x ATR(14) | desk standard for cross systems |
| Trail | 2.0 x ATR(14) chandelier | desk standard |
| Target | none (signal exit) | exits are opposite-cross driven |
| Max hold | 120 bars (~5 days) | desk standard for swing systems |
| Risk fraction | 1% per trade | desk standard |
| Max leverage | 3x | desk standard |
| Costs | 4.5 bps fee + 1 bp slippage | HL reality |

The warmup (120 bars) comfortably exceeds the double-EMA(25,13)
spin-up. Nothing about this strategy was chosen after seeing results;
it is a straight implementation of the 1991 definition plus the
documented territory filter.
