# 3/10 Oscillator — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config. Throwaway sweep script: `/tmp/batch9_calibration.py`
(results only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped (SMA16 trigger) | BTC | 325 | 30.2% | -$5,592 | -4.72 | 0.55 |
| shipped (SMA16 trigger) | ETH | 328 | 29.6% | -$1,337 | -0.47 | 0.91 |
| shipped (SMA16 trigger) | HYPE | 300 | 36.0% | -$1,942 | -1.34 | 0.85 |
| variant (SMA8 trigger) | BTC | 310 | 27.7% | -$5,445 | -5.27 | 0.51 |
| variant (SMA8 trigger) | ETH | 319 | 30.1% | -$3,563 | -2.10 | 0.71 |
| variant (SMA8 trigger) | HYPE | 301 | 42.5% | -$483 | -0.29 | 0.96 |

## One-line verdicts

- **Faster SMA(8) trigger:** HYPE improves to -$483 (win rate 42.5%,
  PF 0.96 — still negative), but BTC is unchanged (-$5,445) and ETH
  gets materially worse (-$3,563, Sharpe -2.10). A faster trigger does
  not fix the exhausted-momentum entry problem; it just trades the same
  losing pattern sooner.
- **Shipped decision:** keep the specified SMA(16) trigger; the sweep is
  diagnostic, not an adoption. Neither variant makes the strategy
  positive on any coin.
