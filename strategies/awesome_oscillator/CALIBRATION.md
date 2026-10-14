# Awesome Oscillator — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-09, same costs/sizing). Two variants against the
shipped config. Throwaway sweep script: `/tmp/ao_sweep_out.txt` (results
only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped AO(5,34) full set | BTC | 235 | 28.1% | -$572 | -0.08 | 0.95 |
| shipped AO(5,34) full set | ETH | 237 | 28.3% | -$1,528 | -0.57 | 0.87 |
| shipped AO(5,34) full set | HYPE | 215 | 29.3% | +$164 | +0.25 | 1.01 |
| cross-only entries | BTC | 217 | 29.0% | -$742 | -0.20 | 0.93 |
| cross-only entries | ETH | 219 | 28.8% | -$521 | -0.07 | 0.96 |
| cross-only entries | HYPE | 204 | 29.9% | +$836 | +0.59 | 1.07 |
| AO(8,21) full set | BTC | 277 | 36.8% | +$615 | +0.47 | 1.05 |
| AO(8,21) full set | ETH | 305 | 28.9% | -$1,867 | -0.80 | 0.87 |
| AO(8,21) full set | HYPE | 257 | 36.6% | +$3,808 | +1.84 | 1.27 |

## One-line verdicts

- **Cross-only entries:** drops the noisy saucer/twin-peak trades, cuts
  churn slightly, and improves HYPE (+$836, Sharpe 0.59) — but BTC and
  ETH stay negative, so it trims losses rather than creating edge.
- **AO(8,21) faster variant:** the only variant with real-looking
  numbers — HYPE +$3,808 (Sharpe 1.84, PF 1.27), BTC +$615 — but it
  craters ETH (-$1,867). That coin-inconsistency is the tell: on one
  7-month in-sample window this is indistinguishable from overfitting,
  so the shipped config stays AO(5,34) until an out-of-sample or
  walk-forward test says otherwise.
- **Shipped decision:** keep the specified AO(5,34) + full signal set as
  the registry config; the sweep is diagnostic, not an adoption. Neither
  variant rescues the strategy across all three coins.
