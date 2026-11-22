# Weekend Crypto Momentum — Calibration

All parameters were fixed **a priori** from the published paper
and 1h-bar reasoning — there is no in-sample sweep, so there is
nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Momentum lookback | 168 bars (7 days) | the paper's 168h momentum; compares each hour with the same hour last week, so the session gate and the lookback are on the same weekly clock |
| Weekend session | Fri 00:00 – Sun 23:59 UTC | the paper's weekend definition, taken verbatim |
| Exit | Monday 00:00 UTC bar | the first bar after the weekend session; the harness executes it at the Monday 01:00 open (1h later than the paper's Sunday 23:59 exit — a harness artifact, not a parameter choice) |
| One entry per weekend | state machine, no re-entry | the paper's trade is a single weekend hold; re-entering after a stop-out converts it into intra-weekend churn (the stateless variant lost −$16,076 in development — see BACKTEST.md) |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2xATR | **deviation from source:** the paper has no stop-loss; the stop and trail are house risk overlays so a bad weekend cannot run unbounded. They can only cut holds short, never extend them |
| Target | None | the thesis is "hold the weekend momentum", not a price level |
| Max hold | 72 bars | the length of one weekend session; a backstop for the Monday exit |
| Risk | 1% / trade, 3x leverage cap | house standard |
| Warmup | 192 bars | 168-bar momentum lag + one day of margin |

The design bet is the paper's: 168h momentum behaves differently
on weekends (markets never sleep, but participants do). The
backtest (BACKTEST.md) is modestly supportive (+$1,210 combined,
105 trades) but the sample is thin and the anomaly is contested
in the 2026 literature — this is a test of the claim, not a
confirmation.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — e.g. shifting the
session boundaries or the lookback until the sample looks good
would be pure overfitting.
