# Ehlers Universal Oscillator — Calibration

Trigger-scale sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The trigger scale is the
oscillator's natural knob: 0.5 is a loose trigger (crosses
fire easily), 0.9 the shipped Ehlers convention, 1.0 a tight
trigger (the trigger is the full prior value). The sweep
re-runs `add_indicators(df, trigger_scale=X)` — the resonator
(period 20, bandwidth 0.3) and the AGC window (100 bars)
stay fixed throughout.

| Trigger scale | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.5 | BTC | 641 | 31.4% | -$6,560 | -4.38 | 0.63 | -$10.23 |
| 0.5 | ETH | 675 | 33.9% | -$3,834 | -1.86 | 0.81 | -$5.68 |
| 0.5 | HYPE | 647 | 34.6% | -$3,002 | -1.44 | 0.87 | -$4.64 |
| 0.9 (shipped) | BTC | 905 | 31.8% | -$7,941 | -6.50 | 0.56 | -$8.78 |
| 0.9 (shipped) | ETH | 908 | 33.6% | -$6,863 | -4.47 | 0.65 | -$7.56 |
| 0.9 (shipped) | HYPE | 905 | 36.0% | -$5,192 | -3.03 | 0.76 | -$5.74 |
| 1.0 | BTC | 942 | 32.8% | -$8,187 | -7.22 | 0.55 | -$8.69 |
| 1.0 | ETH | 933 | 34.9% | -$5,848 | -3.35 | 0.72 | -$6.27 |
| 1.0 | HYPE | 954 | 36.3% | -$4,932 | -2.83 | 0.77 | -$5.17 |

## One-line verdict

- **0.5:** combined -$13,395 on 1,963 trades — the best
  combined read in the sweep by ~$6,600; fewer trades and
  better on every coin than shipped, but still a large loss
  on every coin.
- **0.9:** the shipped setting — combined -$19,996 on 2,718
  trades; the WORST combined read in the sweep, losing the
  most on BTC (-$7,941) and HYPE (-$5,192).
- **1.0:** combined -$18,967 on 2,829 trades — nearly as
  bad as shipped; the tightest trigger trades the most and
  loses almost as much.
- **Shipped decision:** keep the specified trigger scale =
  0.9 as the registry config regardless. It was fixed before
  any backtest was run; the sweep is diagnostic only. The
  shipped setting being the worst of the three is in-sample
  information, and 0.5 still loses -$13,395 — the knob
  changes the size of the loss, not its sign. Do not ship
  a different trigger scale on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The resonator
  is a causal recursion on median price; the AGC RMS uses
  only past bars (expanding window until 100 bars, then
  rolling); the trigger is the prior bar's normalized
  output scaled 0.9; signals compare the current and prior
  bar only; no `ichimoku` chikou column is used anywhere.
  The truncation test (`test_no_lookahead_truncation`)
  confirms indicator and signal values at bar j are
  identical whether computed on the full frame or on the
  frame truncated at j.
- **Source check:** the resonator coefficients, the median-
  price input, the 100-bar RMS AGC normalization, and the
  0.9x delayed trigger are Ehlers' band-pass oscillator as
  cited (TradingView reference implementation per the task
  brief). One documented implementation choice: the RMS
  window uses min_periods=1 (expanding until 100 bars
  accumulate) so bp_norm is defined from the first bar;
  after 100 bars it is exactly the rolling 100-bar RMS.
- **Tests:** 14/14 pass (`python3 -m unittest
  strategies.ehlers_universal_osc.test_ehlers_universal_osc`).
- **No parameter was tuned to PnL.** Trigger scale stays 0.9.
