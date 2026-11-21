# Connors RSI(2) — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| Price RSI | RSI(3) of close (Wilder) | Batch spec; Connors RSI component (a). |
| Streak RSI | RSI(3) of the up/down streak series | Batch spec; component (b). Note the canonical Connors RSI uses RSI(2) here — see §1. |
| Percentile rank | 1-bar ROC ranked over trailing 100 bars, x100 | Batch spec; component (c). Rank counts ROC values strictly below today's, window including today. |
| CRSI | mean of the three components | Connors RSI definition. |
| Long entry / short entry | CRSI crosses below 10 / above 90 (transition only) | Connors' extreme levels. |
| Long exit / short exit | CRSI crosses above 50 / below 50 | Mean-reversion exit at the midpoint. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | Percentile rank needs 100 fully-defined ROC values (first CRSI at bar 100); 120 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped RSI(3)/streak(3)/rank100** | **452** | **-4722.13** | **0.61** | **3155.09** |
| Alt-A rank window 50 | 456 | -5037.44 | 0.60 | 3208.03 |
| Alt-B streak RSI(2) (canonical) | 803 | -6183.63 | 0.66 | 5510.79 |

Per-coin, Alt-A: BTC -2490.82, ETH -1485.39, HYPE -1061.23.
Per-coin, Alt-B: BTC -2957.96, ETH -1812.45, HYPE -1413.22.
Both alternates lose more than the shipped config; the canonical
streak-RSI(2) variant nearly doubles the trade count and loses
more. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Streak RSI period is 3, not the canonical 2.** The batch spec
   says "each on a 3-bar window", so RSI(3) of the streak ships.
   The canonical Connors RSI (Connors Research, 2012) uses
   RSI(3) of price, RSI(2) of the streak, and a 100-bar percentile
   rank. Alt-B runs the canonical 2-period streak RSI: it loses
   more (-$6,183.63) on 803 trades, so the deviation is not what
   costs the strategy its edge here.
2. **Percentile rank counts values strictly below today's ROC**
   in the trailing 100-bar window including today, divided by 100.
   A window containing any undefined (NaN) ROC is skipped, so the
   first CRSI value is at bar 100, not bar 99.
3. **A flat series scores CRSI = 0** (base.rsi fills its
   pre-window values with 0 when there are no gains), so a flat
   stretch sits below 10 without generating an entry — entries
   require a genuine cross from >= 10.
4. **Exits are CRSI 50-crosses only.** A trade entered at CRSI <
   10 can exit only on a cross above 50 (or the harness stop /
   trail / max hold); there is no time-based or 5-bar-MA exit as
   in Connors' original daily system.

## What the exits actually did

Shipped run (452 trades): 349 trades ended on the signal exit
(the 50-cross) and 103 on the harness stop/trail. The signal exit
does the exiting, and it exits late: the win rate is 58% but the
profit factor is 0.61, i.e. the average loss is roughly 1.5x the
average win.

No bug fixes requiring re-runs, no PnL-selected tuning.
