# Point & Figure — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec / textbook, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Box size | 1% of price at column start | Spec. Percentage scaling (StockCharts lists it as a scaling option); keeps boxes proportional across BTC/ETH/HYPE price levels. Recomputed only at column starts so boxes are stable within a column. |
| Reversal | 3 boxes | Spec; the classic Dorsey/StockCharts default. |
| Signal | Double top / double bottom only | Spec; the most basic StockCharts P&F buy/sell signals. Triple tops, catapults, and price objectives deliberately excluded to keep the rule minimal and testable. |
| Price used | Close only | Classic P&F is price-only; using closes keeps the construction causal and unambiguous on 1h bars. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer (same as every batch-21 strategy). |
| WARMUP | 30 | ATR(14) plus margin for the first columns to form. |

No bug fixes requiring re-runs, no PnL-selected tuning. If the box
fraction were tuned on this window it would be overfitting: the box
choice interacts with every signal, and 186 trades is too few to select
it reliably.
