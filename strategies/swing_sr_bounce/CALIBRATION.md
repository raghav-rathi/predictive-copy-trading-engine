# Swing Support / Resistance Bounce — Calibration

All parameters fixed a priori from the S/R spec. No in-sample
sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Zigzag confirmation | 5 bars each side | the house zigzag standard |
| Lookback | 250 bars | levels older than ~10 days are stale |
| Cluster tolerance | 0.5% | two touches must actually be the same level |
| Min touches | 2 | one touch is not a level |
| Touch tolerance | 0.3% | the bar must actually reach the level |
| Failure distance | 0.5% beyond level | a close beyond the level by 0.5% broke it |
| ATR window | 14 | canonical |
| Stop / trail | 1.5xATR / 2xATR | tighter house variant: bounces are quick trades |
| Target | none | the failure exit manages the trade |
| Max hold | 72 bars (~3 days) | a bounce that hasn't bounced in three days is a level that broke |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
