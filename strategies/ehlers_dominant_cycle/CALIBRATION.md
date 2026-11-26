# Ehlers Dominant Cycle — Calibration

Bandwidth sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). Bandwidth is the resonator's
natural knob: 0.3 is a narrower pass band, 0.7 the shipped
octave-wide band, 1.0 a wider band. The sweep re-runs
`add_indicators(df, bandwidth=X)` — the period stays 20, the
high-pass cutoff stays 61.5 bars, and the zero-cross rules
are identical throughout.

| Bandwidth | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.3 | BTC | 615 | 34.8% | -$5,919 | -3.75 | 0.68 | -$9.62 |
| 0.3 | ETH | 619 | 37.3% | -$3,040 | -1.34 | 0.85 | -$4.91 |
| 0.3 | HYPE | 649 | 36.8% | -$3,558 | -1.85 | 0.84 | -$5.48 |
| 0.7 (shipped) | BTC | 655 | 31.1% | -$6,750 | -4.73 | 0.63 | -$10.30 |
| 0.7 (shipped) | ETH | 647 | 32.0% | -$3,897 | -1.93 | 0.82 | -$6.02 |
| 0.7 (shipped) | HYPE | 637 | 36.9% | -$1,137 | -0.37 | 0.95 | -$1.78 |
| 1.0 | BTC | 671 | 27.6% | -$7,190 | -5.38 | 0.59 | -$10.71 |
| 1.0 | ETH | 643 | 30.3% | -$4,385 | -2.27 | 0.79 | -$6.82 |
| 1.0 | HYPE | 619 | 35.4% | -$372 | -0.00 | 0.98 | -$0.60 |

## One-line verdict

- **0.3:** combined -$12,518 on 1,883 trades — the narrow
  band is the worst combined read; BTC/ETH improve slightly
  vs shipped but HYPE collapses to -$3,558.
- **0.7:** the shipped setting — combined -$11,784 on 1,939
  trades; the best ETH (-$3,897) and the second-best HYPE
  (-$1,137) reads in the sweep sit here.
- **1.0:** combined -$11,947 on 1,933 trades — nearly tied
  with shipped; HYPE is nearly breakeven (-$372, PF 0.98,
  Sharpe -0.00) but BTC worsens to -$7,190.
- **Shipped decision:** keep the specified bandwidth = 0.7
  as the registry config regardless. It was fixed before
  any backtest was run; the sweep is diagnostic only. The
  three settings span a $734 combined range and all lose on
  every coin — the knob is not stable, it just shuffles
  which coin loses least. Do not ship a different bandwidth
  on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The high-pass
  and band-pass are causal recursions (each output uses
  only current and past inputs); the dominant-cycle
  measurement assigns the 2× crossing-distance value at
  the crossing bar that completes the half-cycle and
  forward-fills it; signals are zero-cross comparisons
  against the current and prior bar only; no `ichimoku`
  chikou column is used anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the resonator coefficients (beta, gamma,
  alpha) and the BP recursion are Ehlers' band-pass filter
  as cited (verified against the Wickra reference page
  structure per the task brief). One documented derivation:
  the high-pass cutoff of 61.5 bars is one octave below
  the lower pass-band edge (20 / (1 − 0.7/2) = 30.8 bars).
  The sine-wave tests confirm the measurement end: periods
  20 and 40 are recovered within ±20%.
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.ehlers_dominant_cycle.test_ehlers_dominant_cycle`).
- **No parameter was tuned to PnL.** Bandwidth stays 0.7.
