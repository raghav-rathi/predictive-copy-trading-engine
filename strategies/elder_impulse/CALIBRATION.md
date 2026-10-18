# Elder Impulse System — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the shipped
config. Throwaway sweep script: `/tmp/bt_batch9_sweep.py` (ephemeral;
indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped EMA(13) | BTC | 1,174 | 24.5% | -$9,511 | -11.30 | 0.47 |
| shipped EMA(13) | ETH | 1,185 | 22.7% | -$9,270 | -9.57 | 0.51 |
| shipped EMA(13) | HYPE | 1,173 | 29.0% | -$8,263 | -7.61 | 0.55 |
| EMA(21) impulse | BTC | 1,075 | 24.6% | -$9,336 | -10.59 | 0.45 |
| EMA(21) impulse | ETH | 1,073 | 22.6% | -$8,989 | -8.64 | 0.53 |
| EMA(21) impulse | HYPE | 1,064 | 30.4% | -$7,858 | -6.92 | 0.57 |

## One-line verdict

- **EMA(21) impulse:** a slower EMA smooths the color flips slightly (fewer
  trades, marginally smaller losses) but the book stays catastrophic on all
  three coins — PF 0.45–0.57, Sharpe −6.9 to −10.6. The churn is inherent to
  the exit-on-any-flip rule, not to the EMA length; no EMA choice fixes a
  system that exits the moment its two inputs disagree for a single bar.
- **Shipped decision:** keep the specified EMA(13) as the registry config;
  the sweep is diagnostic, not an adoption. The strategy is a reject either
  way.
