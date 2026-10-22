# Ulcer Index Regime Gate — Calibration

Length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing/stops,
120-bar max hold). The sweep re-runs `add_indicators(df, n=X)` only
— signals and risk are unchanged. **The shipped n=14 was fixed a
priori (the canonical Martin length); the sweep is a sensitivity
check, not a selection step — no in-sample selection.**

| Length | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 7 | BTC | 110 | 31.8% | -$649 | -0.38 | 0.89 | -$5.90 |
| 7 | ETH | 102 | 35.3% | +$1,051 | +0.82 | 1.19 | +$10.30 |
| 7 | HYPE | 123 | 34.1% | +$1,196 | +0.90 | 1.16 | +$9.72 |
| 14 (shipped) | BTC | 110 | 31.8% | -$649 | -0.38 | 0.89 | -$5.90 |
| 14 (shipped) | ETH | 102 | 35.3% | +$1,051 | +0.82 | 1.19 | +$10.30 |
| 14 (shipped) | HYPE | 123 | 34.1% | +$1,196 | +0.90 | 1.16 | +$9.72 |
| 28 | BTC | 110 | 31.8% | -$649 | -0.38 | 0.89 | -$5.90 |
| 28 | ETH | 101 | 34.7% | +$1,032 | +0.81 | 1.19 | +$10.22 |
| 28 | HYPE | 114 | 35.1% | +$962 | +0.77 | 1.14 | +$8.44 |

## One-line verdict

The length sweep is nearly a no-op — and that is informative, not
encouraging. The Ulcer Index on 1h crypto bars almost never reaches
the specified thresholds (over the whole window: BTC max 4.38 with
0 bars > 5; ETH 27 bars > 5, 0.51%; HYPE 184 bars > 5, 3.49%; none
ever > 10). So the calm gate passes ~always and the panic exit
never fires: n=7 and n=14 produce literally identical trade sets,
and n=28 differs by a handful of HYPE trades. The strategy as
shipped is effectively a plain 20-bar Donchian breakout / 10-bar
Donchian-low exit long-only system wearing an Ulcer Index costume.

- **Shipped decision:** keep n=14 as specified, fixed a priori. The
  in-sample ranking (14 ≥ 7 > 28 by a hair) is not a justification
  — with the gate this inert, picking 14 over 7 or 28 on
  +$1,598 vs +$1,345 combined would be overfitting to noise anyway.
- **The real finding:** Martin's 5/10 thresholds were calibrated on
  daily equity closes. On 1h crypto bars the UI lives in a 0–4
  band, so the regime gate needs rescaling (e.g., calm < 2.0, panic
  > 4.0, or a percentile-based regime read) before it can do any
  real gating work. That recalibration is out of scope for this
  batch — it would be a parameter change on the backtest window,
  which is exactly what this file refuses to do. Flagged as the
  honest next step for walk-forward work.
