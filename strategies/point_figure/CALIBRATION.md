# Point & Figure — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). One knob: the box-size
multiplier on ATR(14) — 0.25, 0.5 (shipped), 1.0. Throwaway sweep script:
`/tmp/batch7_calib_b.py` (results in `/tmp/batch7_calib_b.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped box 0.5 | BTC | 95 | +$1,019 | +0.72 |
| shipped box 0.5 | ETH | 90 | +$355 | +0.61 |
| shipped box 0.5 | HYPE | 83 | +$704 | +0.88 |
| box 0.25 | BTC | 159 | +$1,212 | +0.86 |
| box 0.25 | ETH | 163 | −$1,493 | −0.35 |
| box 0.25 | HYPE | 174 | +$309 | +0.61 |
| box 1.0 | BTC | 40 | +$3,988 | +2.52 |
| box 1.0 | ETH | 40 | −$970 | −0.83 |
| box 1.0 | HYPE | 50 | −$184 | +0.18 |

## One-line verdicts

- **Box 0.25:** smaller boxes = more columns, more reversals, more
  churn (496 trades). BTC improves slightly, but ETH collapses −$1,493
  — the extra sensitivity just manufactures whipsaws.
- **Box 1.0:** the BTC +$3,988 / Sharpe +2.52 looks spectacular and is
  exactly the kind of number to distrust: 40 trades, and ETH/HYPE go
  negative. Big boxes = few, lucky breakouts. Sample-size suspect;
  not shipped.
- **Verdict:** the shipped 0.5 is the only variant positive on all three
  coins with 83–95 trades each. Shipped config stands; no variant
  promoted.
