# Ehlers MAMA/FAMA Cross — Calibration

fastLimit sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing, 2xATR stop,
200-bar max hold). fastLimit is the ceiling on the adaptive alpha:
higher = MAMA tracks price more tightly (faster, more crosses); lower
= MAMA stays closer to the slow limit (smoother, fewer crosses).

| fastLimit | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.5 (shipped) | BTC | 568 | 23.8% | -$5,409 | -3.28 | 0.69 | -$9.52 |
| 0.5 (shipped) | ETH | 574 | 25.6% | -$5,141 | -2.88 | 0.69 | -$8.96 |
| 0.5 (shipped) | HYPE | 518 | 30.5% | -$1,359 | -0.55 | 0.93 | -$2.62 |
| 0.4 | BTC | 477 | 22.6% | -$5,943 | -3.81 | 0.62 | -$12.46 |
| 0.4 | ETH | 480 | 23.5% | -$5,154 | -2.94 | 0.68 | -$10.74 |
| 0.4 | HYPE | 428 | 32.7% | +$1,920 | +1.04 | 1.10 | +$4.49 |
| 0.6 | BTC | 719 | 25.5% | -$7,210 | -5.59 | 0.60 | -$10.03 |
| 0.6 | ETH | 663 | 27.0% | -$5,388 | -3.26 | 0.71 | -$8.13 |
| 0.6 | HYPE | 609 | 33.0% | -$1,651 | -0.78 | 0.92 | -$2.71 |

## One-line verdict

- **0.4:** the in-sample winner (combined -$9,177 vs -$11,909 at 0.5
  vs -$14,249 at 0.6) — HYPE turns genuinely positive (+$1,920,
  Sharpe +1.04, PF 1.10) with fewer, smoother trades. But BTC is *worse*
  at 0.4 than at 0.5, so the win is one-coin only.
- **0.6:** uniformly worst — more crosses (719 BTC trades), deeper
  losses, BTC Sharpe -5.59. Faster alpha just means faster whipsaw.
- **Shipped decision:** keep the specified fastLimit=0.5. The 0.4
  setting beats it in-sample on this exact window, and the in-sample
  winner was explicitly **not** adopted — picking 0.4 now would be
  pure in-sample selection on a 7-month window where every setting
  loses on BTC/ETH. The honest read: fastLimit is a real sensitivity
  knob (slower = fewer, smoother trades), but the knob moves a losing
  strategy between shades of red; it needs a structural fix (or a
  different timeframe), not a parameter tweak.
