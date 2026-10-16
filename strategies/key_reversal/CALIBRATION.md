# Key reversal — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). Two knobs: the volume
filter on/off and the pattern lookback (10 vs 20 bars). Throwaway sweep
script: `/tmp/batch7_calib_b.py` (results in `/tmp/batch7_calib_b.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped vol-off lb20 | BTC | 34 | −$310 | −0.46 |
| shipped vol-off lb20 | ETH | 26 | +$1,263 | +1.79 |
| shipped vol-off lb20 | HYPE | 43 | +$928 | +1.32 |
| vol-on lb20 | BTC | 19 | −$193 | −0.37 |
| vol-on lb20 | ETH | 19 | +$1,681 | +2.43 |
| vol-on lb20 | HYPE | 20 | −$907 | −2.25 |
| vol-on lb10 | BTC | 29 | −$18 | +0.02 |
| vol-on lb10 | ETH | 32 | +$1,396 | +1.82 |
| vol-on lb10 | HYPE | 27 | −$976 | −2.02 |
| vol-off lb10 | BTC | 56 | −$738 | −0.94 |
| vol-off lb10 | ETH | 55 | +$1,874 | +1.69 |
| vol-off lb10 | HYPE | 64 | +$817 | +1.00 |

## One-line verdicts

- **Volume filter ON:** the best single-coin print in the whole sweep
  (ETH +$1,681, Sharpe +2.43) — and HYPE goes deeply negative (−$907 /
  −$976). The filter concentrates on high-volume exhaustion bars, which
  worked on ETH's structure and failed on HYPE's. Inconsistent across
  coins; not shipped.
- **Volume filter OFF:** positive on ETH and HYPE at both lookbacks,
  mildly negative on BTC. The 10-bar lookback makes the most money
  combined (+$1,953) but with worse BTC (−$738) and lower Sharpes;
  the 20-bar lookback is the better risk-adjusted cross-coin compromise
  (ETH Sharpe 1.79, HYPE 1.32, BTC only −3.1%).
- **Verdict:** ship the unfiltered 20-bar variant. It is the most
  consistent across coins, keeps the classic 20-bar definition, and the
  combined +$1,881 is within noise of the lb10 total. The volume filter
  is implemented in the code (`use_volume_filter` flag) but defaults
  off.
