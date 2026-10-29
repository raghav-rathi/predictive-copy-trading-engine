# Keltner Pullback — Calibration

All parameters fixed a priori from the Keltner channel spec
and standard trend-filter practice. No in-sample sweep,
nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Keltner midline | EMA20 | Keltner's original midline construction |
| Keltner ATR | ATR(10), multiplier 1.5 | the channel bands frame the pullback zone; the midline itself is the trigger |
| Trend filter | EMA50, must be rising (long) / falling (short), price on the trend side | a pullback is only a pullback inside a surviving trend |
| Entry trigger | close crosses back over the midline | the cross proves the dip happened and is reversing |
| Exit | opposite midline cross | a second cross is the thesis failing, not a deeper pullback |
| ATR window (risk) | 14 | canonical |
| Stop / trail | 2xATR / 3xATR | roomy stop (pullbacks are noisy), long trail to let resumed trends run |
| Target | none | the opposite-cross exit manages the trade |
| Max hold | 120 bars (~5 days) | a pullback that has not resumed in five days was a reversal |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the failure mode is frequency, not
calibration — the midline cross fires on every minor
oscillation, and no plausible stop/trail change fixes a
signal that is mostly chop. The only change with a real story
would be requiring the pullback to actually reach a deeper
level (e.g. the lower band, or a minimum dip size in ATR)
before the re-cross counts — that is a different strategy
(a band-touch pullback, not a midline pullback) and was not
tested here; it must not be fitted to this window.

**Verdict: loser, badly.** -$11,461 combined over 1,253
trades, red on all three coins, worst max drawdown -55.6%
(BTC). Do not trade this as shipped.
