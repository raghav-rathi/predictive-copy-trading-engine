# Tasuki Gap Pattern — Calibration

All parameters fixed a priori from the Nison tasuki
definition, except the one documented adaptation below. No
in-sample sweep, nothing selected on the backtest window's
PnL (the adaptation was chosen on signal counts, before any
PnL was computed for it).

| Parameter | Value | Rationale |
|---|---|---|
| Gap | o2 > c1 (upside) / o2 < c1 (downside) | body gap in the trend direction |
| First two bodies | each >= 0.5 * range | gap candles must be decisive |
| Third candle open | inside the second candle's body | textbook tasuki placement |
| Third candle close (ADAPTED) | between the first candle's close and the second candle's close | see below |
| Trend filter | first close vs close 5 bars earlier, in the trend direction | a continuation pattern needs a trend to continue |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a continuation to resume |
| Target | none | the opposite-tasuki exit manages the trade |
| Max hold | 120 bars (~5 days) | longer leash than the reversal patterns: continuations ride |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Why the adaptation exists (diagnostic, not tuning):** with
the textbook third-close rule (close strictly between the
first close and the second open), the funnel on this window
is: gap + two strong same-color candles + counter-color
third candle + open inside the second body = 24 / 20 / 28
candidates (BTC / ETH / HYPE, upside), of which ZERO close
inside the literal gap. The gaps are tiny: median $1.00 on
BTC (~0.3% of a candle's range), $0.10 on ETH, $0.003 on
HYPE. Requiring a close inside a sub-tick interval is not a
pattern, it is a lottery ticket. The shipped rule keeps the
two properties that make a tasuki a tasuki — a gap in the
trend direction, and a counter-color pullback that does not
violate the first candle's close — and measures the pullback
against the second candle's close. It yields 15 / 20 / 33 raw
signals per coin, a tradeable sample.

Sensitivity note: the trend filter and the strong-body rule
do most of the filtering before the close rule; dropping
either would roughly double signals with weaker trend
quality. The 120-bar hold rarely binds (39 of 42 exits are
stops, not max-hold or signal exits), so hold length is not
the lever here — stop placement is.

**Verdict: no demonstrated edge.** +$238 combined over 42
trades (PF 1.14) is noise on $30k capital. Do not trade this
as shipped.
