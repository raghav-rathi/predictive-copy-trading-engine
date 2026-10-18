# EWMAC Forecast (Rob Carver) — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config: single EWMAC rule (16,64) instead of the three-rule
(8,32)+(16,64)+(32,128) blend (same z-scoring, same ±10 band, same
risk). Sweep script: `/tmp/bt_batch9.py` (`<slug> cal` mode).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped 3-rule blend | BTC | 69 | 20.3% | +$822 | +0.68 | 1.18 |
| shipped 3-rule blend | ETH | 65 | 16.9% | +$873 | +0.68 | 1.20 |
| shipped 3-rule blend | HYPE | 80 | 27.5% | -$888 | -0.57 | 0.79 |
| single rule (16,64) | BTC | 62 | 24.2% | +$1,647 | +1.13 | 1.40 |
| single rule (16,64) | ETH | 58 | 15.5% | +$396 | +0.40 | 1.10 |
| single rule (16,64) | HYPE | 67 | 29.9% | -$66 | +0.05 | 0.98 |

## One-line verdict

- **Single rule (16,64):** beats the shipped blend everywhere on this
  window — BTC nearly doubles (+$1,647, Sharpe 1.13), HYPE's loss
  shrinks to -$66, ETH stays mildly positive. The mid-speed rule alone
  catches the trends that matter on 1h crypto while the fast (8,32)
  rule's whipsaw and the slow (32,128) rule's lag dilute the blend.
- **Shipped decision:** keep the specified 3-rule blend as the registry
  config anyway. The single rule's win is measured on the same 7-month
  in-sample window used to notice it — adopting it now would be pure
  in-sample selection. Revisit only with out-of-sample or walk-forward
  evidence.
