# MESA Sine Wave — Calibration

I2/Q2 smoothing sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The smoothing factor is the
strategy's natural knob: how heavily the in-phase and
quadrature components are smoothed before the phase is taken
— 0.1 is sluggish, 0.4 is reactive. The sweep re-runs
`add_indicators(df, smooth=X)` only — signals and risk are
unchanged.

| Smooth | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.1 | BTC | 884 | 38.7% | -$7,224 | -5.60 | 0.64 | -$8.17 |
| 0.1 | ETH | 889 | 42.2% | -$5,130 | -2.99 | 0.79 | -$5.77 |
| 0.1 | HYPE | 850 | 45.1% | -$2,830 | -1.44 | 0.89 | -$3.33 |
| 0.2 (shipped) | BTC | 972 | 39.8% | -$7,415 | -5.95 | 0.67 | -$7.63 |
| 0.2 (shipped) | ETH | 950 | 43.3% | -$4,875 | -2.73 | 0.79 | -$5.13 |
| 0.2 (shipped) | HYPE | 912 | 45.8% | -$2,883 | -1.44 | 0.89 | -$3.16 |
| 0.4 | BTC | 1,058 | 40.5% | -$7,637 | -6.30 | 0.65 | -$7.22 |
| 0.4 | ETH | 1,066 | 42.7% | -$6,130 | -3.85 | 0.72 | -$5.75 |
| 0.4 | HYPE | 1,019 | 44.7% | -$3,070 | -1.57 | 0.87 | -$3.01 |

## One-line verdict

- **0.1:** combined -$15,183 (2,623 trades) — fewest trades,
  same catastrophe. Slower smoothing does not calm the phase.
- **0.2:** the shipped setting — combined -$15,174 (2,834
  trades), the least-bad of the three by $9, which is noise.
- **0.4:** combined -$16,837 (3,143 trades) — most trades,
  worst combined; more reactive components cross more often.
- **Shipped decision:** keep the specified smoothing 0.2 as
  the registry config regardless. It was fixed before any
  backtest was run; the sweep shows the knob moves the
  combined result by ~$1.7k on a ~$15k loss and never
  approaches breakeven, so there is nothing here to adopt —
  and adopting the least-bad value because it is least-bad
  in-sample would still be in-sample selection. The honest
  read: the sine/lead-sine cross itself is structurally
  unsuited to 1h crypto, at any smoothing.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. The smoother,
  detrender, quadrature and jI/jQ filters read only current
  and lagged bars (lags up to 6 within each filter stage, all
  backward); the (0.075*Period[1] + 0.54) factor uses the
  previous bar's period; the homodyne discriminator reads
  I2/Q2 at bars i and i−1 only; signals use
  `crossed_above`/`crossed_below` on bars i and i−1 only.
  The truncation test (`test_no_lookahead_truncation`)
  confirms indicator and signal values at bar j are identical
  whether computed on the full frame or on the frame truncated
  at j. Ehlers' original uses arctan(Im/Re) for the
  discriminator; this build uses atan2(Im, Re), the same
  discriminator with correct quadrants — a deliberate,
  documented choice, not a deviation in the signal logic.
- **Source check:** the ArrowAlgo MESA Sine Wave guide
  (verified URL, given in the batch-46 brief) confirms the
  4-bar WMA smoother, the 0.0962/0.5769 Hilbert coefficients,
  I1 = detrender lagged 3, the homodyne discriminator with
  period clamped 6..50, and sine vs lead sine (45-degree
  lead). The implementation follows it as specified.
- **Tests:** 13/13 pass (`python3 -m unittest
  strategies.mesa_sine_wave.test_mesa_sine_wave`).
- **No parameter was tuned to PnL.** Smoothing stays 0.2.
