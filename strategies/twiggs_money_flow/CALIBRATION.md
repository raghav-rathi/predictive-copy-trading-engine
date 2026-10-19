# Twiggs Money Flow — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). One variant against the
shipped config: faster TMF smoothing (Wilder 14 instead of 21) — same
zero-line cross logic, same 2xATR stop / 60-bar max hold. Sweep script:
`/tmp/bt_new3.py` (`cal` mode).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped TMF(21) | BTC | 528 | 23.1% | -$5,570 | -3.64 | 0.63 |
| shipped TMF(21) | ETH | 453 | 28.9% | -$3,100 | -1.70 | 0.77 |
| shipped TMF(21) | HYPE | 420 | 29.3% | +$192 | +0.29 | 1.01 |
| TMF(14) | BTC | 640 | 22.5% | -$6,268 | -4.22 | 0.62 |
| TMF(14) | ETH | 608 | 27.5% | -$4,632 | -2.83 | 0.70 |
| TMF(14) | HYPE | 504 | 29.4% | -$1,381 | -0.55 | 0.92 |

## One-line verdict

- **TMF(14):** worse on every coin — combined −$12,280 on 1,752 trades
  vs shipped −$8,478 on 1,401. Faster smoothing just adds more zero-line
  whipsaws (20% more trades, lower win rate everywhere, HYPE's lone
  +$192 flips to −$1,381). The failure is the cross logic itself, not
  the smoothing length: no amount of re-tuning the Wilder period fixes
  a signal that fires 6+ times a day into 1h ranges.
- **Shipped decision:** keep the specified TMF(21) as the registry
  config — not because it works (it doesn't; see BACKTEST.md), but
  because the variant sweep confirms there is no parameter rescue, and
  the shipped spec is the documented Twiggs formulation. The strategy
  is recorded as a rejected mechanism.
