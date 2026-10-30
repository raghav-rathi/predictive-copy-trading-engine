# DMI Cross — Calibration

All parameters fixed a priori from Wilder's Directional
Movement definition and the house standard. No in-sample
sweep, nothing selected on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| DI / ADX period | 14 | Wilder's canonical period, as in the source |
| ADX entry gate | > 20 | Wilder's no-trend line (ADX < 20 = no trend); 25 would be the "strong trend" line, 20 is the looser spec gate |
| Entry | DI cross + ADX gate | the classic DMI signal, trend-filtered |
| Exit | opposite DI cross, ungated | a crossed DI pair no longer supports the open side, whatever ADX says |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house standard, roomy for a trend trade |
| Target | none | the opposite cross manages the trade |
| Max hold | 120 bars (~5 days) | house standard; never bound (0 max-hold exits) |
| Risk | 1% / trade, 3x leverage cap | house standard |
| WARMUP | 40 | ADX first valid at bar 26 (DI 14 + DX + ADX smoothing 14), plus margin |

Sensitivity note: the max-hold never binds and the trail
rarely gets room to work — 303 of 552 exits are hard stops.
The binding constraint is signal quality, not risk
parameters: raising the ADX gate toward 25 would cut trade
count but would also be a post-hoc change on this window,
so it is NOT adopted. The honest read is that the 1h DI
cross has no edge here; no parameter in this table rescues
a 25.9% win rate.

**Verdict: loser.** −$4,709 combined over 552 trades
(PF 0.57–0.94 per coin). Do not trade this as shipped.
