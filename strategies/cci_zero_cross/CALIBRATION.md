# CCI Zero Cross — Calibration

All parameters fixed a priori from the Lambert CCI spec and
the standard trend-filter setup. No in-sample sweep, nothing
selected on the backtest window. This strategy is distinct
from the existing CCI strategies by construction: it trades
neither divergence (cci_divergence) nor the +/-100 extremes
(cci_extreme) — the zero line plus the trend filter are the
entire signal.

| Parameter | Value | Rationale |
|---|---|---|
| CCI period | 20 | Lambert's original period, unchanged |
| Mean deviation | rolling window's own mean (TA-Lib definition) | same construction as cci_extreme, so the two are directly comparable |
| Trend filter | SMA(50) of close | crosses against the trend are ignored; only with-trend regime flips trade |
| Exit | opposite zero cross, no level filter | the zero line is the whole thesis — a cross back is a failed regime |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 3xATR | roomier trail than the mean-reversion strategies, since these are trend-continuation trades |
| Max hold | 240 bars (~10 days) | trend legs get time to develop |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the failure is a frequency problem, not a
threshold problem — 920 trades in ~7.5 months means the zero
line is crossed constantly on 1h bars, and the SMA(50) filter
passes roughly half of them. Requiring CCI to hold beyond zero
for N bars before entry would cut the whipsaw count, but it
would also convert the signal from a regime flip into a
lagging confirmation, and it was not tested here and must not
be fitted to this window.

**Verdict: loser.** -$9,926 combined over 920 trades, 24.9%
win rate, red on all three coins. Do not trade this as
shipped.
