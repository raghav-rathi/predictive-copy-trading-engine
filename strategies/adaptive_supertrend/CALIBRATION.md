# Adaptive Supertrend — Calibration

Fixed-k sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same costs/sizing, 2xATR stop,
3xATR trail, 200-bar max hold). The sweep re-runs the adaptive loop
with a constant k series — signals and risk unchanged — so each row is
what plain Supertrend(10, k) would have done. The adaptive row is the
shipped config.

| Setting | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| k=2.0 fixed | BTC | 202 | 33.7% | -$1,346 | -0.74 | 0.86 | -$6.66 |
| k=2.0 fixed | ETH | 206 | 36.4% | +$233 | +0.26 | 1.02 | +$1.13 |
| k=2.0 fixed | HYPE | 214 | 34.6% | +$432 | +0.44 | 1.03 | +$2.02 |
| k=2.0 fixed | **Combined** | **622** | — | **-$681** | — | — | — |
| k=3.0 fixed | BTC | 129 | 30.2% | -$2,497 | -2.20 | 0.64 | -$19.36 |
| k=3.0 fixed | ETH | 137 | 30.7% | -$1,895 | -1.55 | 0.74 | -$13.83 |
| k=3.0 fixed | HYPE | 132 | 37.1% | +$2,313 | +1.56 | 1.30 | +$17.52 |
| k=3.0 fixed | **Combined** | **398** | — | **-$2,080** | — | — | — |
| k=4.0 fixed | BTC | 86 | 33.7% | +$22 | +0.11 | 1.01 | +$0.26 |
| k=4.0 fixed | ETH | 93 | 33.3% | -$486 | -0.36 | 0.91 | -$5.23 |
| k=4.0 fixed | HYPE | 78 | 42.3% | +$989 | +0.99 | 1.24 | +$12.68 |
| k=4.0 fixed | **Combined** | **257** | — | **+$524** | — | — | — |
| adaptive (shipped) | BTC | 145 | 33.8% | -$1,988 | -1.56 | 0.74 | -$13.71 |
| adaptive (shipped) | ETH | 153 | 30.7% | -$1,281 | -0.91 | 0.83 | -$8.38 |
| adaptive (shipped) | HYPE | 144 | 36.1% | +$3,379 | +2.06 | 1.36 | +$23.47 |
| adaptive (shipped) | **Combined** | **442** | — | **+$110** | — | — | — |

## One-line verdict

- **k=2.0 (tight):** the whipsaw setting — 622 trades, the most of
  any row, combined -$681. Tight bands flip constantly on 1h noise.
- **k=3.0 (classic default):** the worst combined row (-$2,080) —
  BTC -$2,497 at Sharpe -2.20 is the single worst coin-setting in the
  sweep. The default is not the safe choice on this window.
- **k=4.0 (wide):** the best combined row (+$524) and the only
  setting with BTC flat-to-green — wider bands mean fewer, later
  flips, and 1h crypto rewards patience here. But it is still only
  +$524 over 257 trades, and ETH stays red.
- **Adaptive (shipped):** +$110, between k=3 and k=4. The adaptation
  does not beat the best fixed setting — it buys HYPE performance
  (+$3,379, the best HYPE row) at the cost of BTC/ETH, because the
  tight k=2 regime fires exactly when BTC/ETH are chopping.
- **How often does the adaptation engage?** k=3.0 covers 80.0% of
  BTC bars, 76.0% of ETH, 81.9% of HYPE; k=2.0 covers 12.6% / 14.7% /
  7.5%; k=4.0 covers 7.4% / 9.3% / 10.5%. Mean chop is 49.3 / 48.9 /
  50.9 — mid-range most of the time, so the adaptive layer is a
  ~20%-of-bars overlay, not a regime switch.
- **Shipped decision:** keep the specified chop thresholds (38/62)
  and k values (2/3/4) as the registry config regardless. They were
  fixed a priori from the published sources — Dreiss's levels, the
  standard Supertrend multiplier range — not chosen from this sweep,
  and leaning toward k=4 *because* it wins in-sample would be
  in-sample selection on a 7-month window where HYPE carried
  everything anyway. The honest read: the multiplier moves which coin
  pays, not whether the strategy works — that still needs walk-forward
  or out-of-sample evidence.
