# Gann Square of Nine — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Grid step | 0.25 in √price (45°) | Spec: L = (floor(s·4)/4 + 0.25·j)², j = 0..8. Verified against the published formula Level = (√p ± θ/180)² (PatternsWizard, Forexop, TradingView Sq9 scripts). |
| Entry filter | Level within 0.5% of the prior close | Spec. |
| Exits | Back below/above entry level, or next level up/down | Spec; entry level and target are tracked as causal entry-bar state in signals.py. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup + margin (levels need only 1 prior bar; 50 is margin). |

Spec interpretation recorded: "level within 0.5% of price" was read
as within 0.5% of the *prior* close, the price the nearest level is
defined against. No other reading was tested. Note the consequence:
ladder spacing in percent terms is ≈ 0.5/√p, so the filter is nearly
always satisfied on BTC (~0.18% spacing), about half the time on ETH
(~1% spacing), and rarely on HYPE (~11% spacing) — the strategy's
trade frequency is therefore mostly a function of coin price, not of
market behaviour. That is a property of the briefed rule, not a bug,
and it was left as specified.

No bug fixes requiring re-runs, no PnL-selected tuning.
