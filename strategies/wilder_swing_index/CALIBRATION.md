# Wilder Swing Index / ASI — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the shipped
config. Throwaway sweep script: `/tmp/bt_batch9_sweep.py` (ephemeral;
indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped window 20 | BTC | 216 | 27.8% | -$3,449 | -2.03 | 0.73 |
| shipped window 20 | ETH | 212 | 25.9% | -$2,027 | -0.92 | 0.84 |
| shipped window 20 | HYPE | 209 | 30.1% | -$1,856 | -0.97 | 0.83 |
| window 30 | BTC | 171 | 29.2% | -$3,030 | -1.92 | 0.72 |
| window 30 | ETH | 172 | 26.2% | -$2,430 | -1.30 | 0.77 |
| window 30 | HYPE | 175 | 28.0% | -$2,110 | -1.18 | 0.79 |

## One-line verdict

- **Window 30:** fewer, more selective breakouts (171–175 trades vs ~212)
  and slightly smaller losses, but still negative on all three coins with
  PF 0.72–0.79. A wider window filters some chop but does not create the
  missing edge — the breakout entries still buy exhaustion more often than
  continuation.
- **Shipped decision:** keep the specified 20-bar window as the registry
  config; the sweep is diagnostic, not an adoption. The strategy is a reject
  either way.
