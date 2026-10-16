# episodic_thrust — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two parameters: base
tightness {3, 4, 5x ATR} × thrust range {2.0, 2.5x ATR}. Runner:
`/tmp/batch7_run.py` (results in `/tmp/batch7_results.json`).

**Important:** the daily-original tightness of 1.2x ATR produces ZERO
trades on hourly crypto (a 30-bar hourly range runs ~5.6x ATR at the
median), so the shipped hourly adaptation already uses 4.0x — the
bottom quartile of hourly coil tightness.

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (tight 4, rng 2.0) | BTC | 5 | −$227 | −2.46 |
| shipped (tight 4, rng 2.0) | ETH | 2 | +$56 | +1.19 |
| shipped (tight 4, rng 2.0) | HYPE | 1 | +$209 | +1.92 |
| tight 3, rng 2.0 | BTC | 2 | −$121 | −1.69 |
| tight 3, rng 2.0 | ETH | 0 | $0 | 0.00 |
| tight 3, rng 2.0 | HYPE | 0 | $0 | 0.00 |
| tight 3, rng 2.5 | BTC | 1 | −$97 | −1.58 |
| tight 3, rng 2.5 | ETH | 0 | $0 | 0.00 |
| tight 3, rng 2.5 | HYPE | 0 | $0 | 0.00 |
| tight 4, rng 2.5 | BTC | 2 | −$118 | −1.81 |
| tight 4, rng 2.5 | ETH | 1 | +$20 | +1.00 |
| tight 4, rng 2.5 | HYPE | 1 | +$209 | +1.92 |
| tight 5, rng 2.0 | BTC | 10 | −$293 | −2.22 |
| tight 5, rng 2.0 | ETH | 5 | −$117 | −1.09 |
| tight 5, rng 2.0 | HYPE | 4 | +$180 | +1.10 |
| tight 5, rng 2.5 | BTC | 5 | −$130 | −1.43 |
| tight 5, rng 2.5 | ETH | 3 | −$125 | −1.30 |
| tight 5, rng 2.5 | HYPE | 2 | +$271 | +2.09 |

## One-line verdicts

- **Tighter is not better here:** tight 3 kills the signal entirely on
  ETH/HYPE (0 trades) — the base filter becomes a no-trade filter.
- **Looser (tight 5) doubles the sample but adds losers:** 19 trades
  vs 8, and BTC/ETH both bleed — the extra "bases" are just chop, not
  neglect.
- **Verdict:** no variant produces a trade count worth judging. The
  shipped config (tight 4, range 2.0) stands as the documented
  adaptation; the honest conclusion is that this proxy needs years of
  data or a real catalyst feed, not parameter tuning.
