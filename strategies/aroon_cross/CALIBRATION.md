# Aroon Cross — Calibration

All parameters fixed a priori from Chande's Aroon definition
and the house standard. No in-sample sweep, nothing selected
on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Aroon period | 25 | Chande's default, as in the source |
| Entry gate | crossing line > 70 | fresh extremes: a high/low within ~7 of the last 25 bars; 50 would admit range drift |
| Entry | Aroon cross + gate | the classic Aroon trend-emergence signal |
| Exit | opposite cross, ungated | the trend-emergence signal reversing |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house standard |
| Target | none | the opposite cross manages the trade |
| Max hold | 120 bars (~5 days) | house standard; never bound (0 max-hold exits) |
| Risk | 1% / trade, 3x leverage cap | house standard |
| WARMUP | 30 | Aroon(25) plus margin |
| Tie rule | most recent high/low | "bars since the most recent high/low" per the source definition |

Sensitivity note: the > 70 gate is doing real work — the
bare cross without it would fire far more often in ranges —
but it does not create an edge: 516 of 588 exits are still
stops. The binding problem is follow-through, not gate
level, and moving the gate on this window's numbers would
be post-hoc tuning, so it is NOT adopted.

**Verdict: no demonstrated edge.** +$119 combined over 588
trades (PF 0.80–1.10 per coin) is noise. Do not trade this
as shipped.
