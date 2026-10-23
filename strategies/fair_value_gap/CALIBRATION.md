# Fair Value Gap Retest — Calibration

All parameters were fixed **a priori** from the ICT rule as written —
there is no sweep and no in-sample selection in this file, by design
(the task brief specified the full mechanism up front):

| Parameter | Value | Basis |
|---|---|---|
| Displacement threshold | 1.5 × ATR(14) | brief-specified; "impulsive" middle candle |
| ATR length | 14 | canonical Wilder length |
| Long entry | dip into gap (`l < fvg_high`) + close back above (`c > fvg_high`) | the ICT rejection bar |
| Short entry | mirror | symmetric |
| Long exit | zone mitigated (`l < fvg_low`) or opposite signal | "stop beyond the far edge" |
| Stop | 2.0 × ATR | wide, approximating "beyond the far edge + buffer" (harness limitation, documented in README) |
| Trail | 2.0 × ATR chandelier | lets a confirmed retest run |
| Target | none | exits are signal-driven |
| Max hold | 72 bars (~3 days) | retests either work or don't |
| Risk / leverage | 1% / 3x | desk standard |
| Fees | 0.045% + 0.01% slippage per side | Hyperliquid base |

The one deliberate interpretation choice (documented in signals.py):
the strict inequalities `<`/`>` on the entry exclude the formation
bar itself (where `l[i] ≡ fvg_high` by construction), so entries are
genuine later-bar retests. The literal `<=`/`>=` reading would enter on
the displacement bar's own close — trend-chasing, not the ICT retest.

## Post-hoc observation (not a parameter change)

The displacement filter is far too permissive on 1h crypto: zones are
active on 53–61% of bars (BTC 61.4%, ETH 60.7%, HYPE 53.4%). On the
higher timeframes ICT targets, a true displacement gap is a rare
institutional footprint; on 1h crypto, 1.5×ATR is an ordinary bar.
Rescaling the filter (higher displacement multiple, higher-timeframe
context, or a displacement percentile) would be a parameter change on
the backtest window — exactly what this file refuses to do. Flagged
for walk-forward work, not tuned here.
