# KAMA trend — Calibration (robustness sweep)

Same data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
2026-10-10). Two parameter variants vs the shipped config, run with a
throwaway `/tmp/kama_sweep.py` (not committed; it only flips the module
constants `indicators.N` / `indicators.ER_MIN` and re-runs the same
harness).

## Variant table (net $ per coin + combined)

| Variant | BTC | ETH | HYPE | Combined trades | Combined net $ |
|---|---|---|---|---|---|
| base (n=10, ER>0.3) | -$2,161 | -$665 | +$886 | 438 | -$1,940 |
| n=14 ER window (ER>0.3) | -$553 | -$976 | +$1,579 | 264 | +$50 |
| ER filter 0.2 (n=10) | -$2,168 | -$1,087 | +$1,298 | 800 | -$1,957 |

HYPE detail: base Sharpe +1.11 / PF 1.22; n=14 Sharpe +2.02 / PF 1.73;
ER-0.2 Sharpe +1.35 / PF 1.20.

## One-line verdicts

- **base (shipped):** mixed — HYPE edge (+$886, PF 1.22) is real in-sample,
  BTC/ETH whipsaw through the 2026 chop; combined -$1,940.
- **n=14 ER window:** the only variant that doesn't lose money overall
  (+$50 combined, 264 trades); longer efficiency window filters more
  chop and the HYPE edge roughly doubles (Sharpe 2.02) — candidate for
  a walk-forward / out-of-sample check before any promotion.
- **ER filter 0.2:** loosening the efficiency filter nearly doubles trade
  count (800 vs 438) and worsens the combined result (-$1,957); the 0.3
  filter is doing real work — do not loosen it.

## Note

No variant turned BTC/ETH positive, so the mechanism's edge in this
window is coin-selective (HYPE), not universal. The n=14 result is
in-sample on the same window and needs out-of-sample validation before
it means anything.
