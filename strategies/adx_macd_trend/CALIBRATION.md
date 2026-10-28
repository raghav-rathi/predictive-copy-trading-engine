# ADX + MACD Trend — Calibration

## Parameter choices

| Parameter | Value | Why |
|---|---|---|
| ADX period | 14 | Wilder's standard; matches the ATR window so both read the same trend clock. |
| ADX entry threshold | 25 | Textbook "trend exists" level. Lower (20) admits more chop; higher (30) waits longer and enters later. |
| ADX exit threshold | 20 | Textbook "trend gone" level, set below the entry level so a single dip under 25 does not exit immediately — a hysteresis band of 20–25. |
| MACD | 12 / 26 / 9 | Appel's standard. No tuning. |
| Stop / trail | 2.0x / 2.5x ATR | Batch standard; gives trend trades room while the chandelier locks in extended moves. |
| Max hold | 168 bars (~7 days) | Caps stale trend trades; a trend that has not paid in a week is not paying. |
| Risk / leverage | 1% / 3x | Batch standard. |

## Sensitivity note

The result is not knife-edge on the ADX thresholds: the loss is
spread across all three coins with win rates in the 26–33% band,
so moving the entry gate from 25 to 20 or 30 would change trade
count, not the sign of the outcome — the underlying problem is
MACD-cross timing at 1h, not the gate level. This was not tested
by re-running tuned variants (that would be window-fitting); it
is a read on how uniform the loss is.

## Verdict: loser

Ship as a documented loser. The honest conclusion is that
ADX-gated MACD crosses do not survive 1h crypto in this window.
Do not "fix" it by tuning thresholds on this data.
