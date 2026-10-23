# RSI divergence — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). Two parameters: the
oversold/overbought trigger at the second extreme (35/65 vs 40/60)
and the confirmation re-cross level (30/70 vs 35/65). Throwaway sweep
script: `/tmp/batch7_calibrate.py` (results in `/tmp/batch7_calib.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped trig35/conf30 | BTC | 5 | −$385 | −1.51 |
| shipped trig35/conf30 | ETH | 9 | −$430 | −1.55 |
| shipped trig35/conf30 | HYPE | 8 | −$589 | −2.48 |
| trig35/conf35 | BTC | 7 | +$644 | +1.43 |
| trig35/conf35 | ETH | 16 | −$1,088 | −3.08 |
| trig35/conf35 | HYPE | 18 | −$6 | +0.03 |
| trig40/conf30 | BTC | 10 | −$837 | −2.56 |
| trig40/conf30 | ETH | 10 | −$258 | −0.81 |
| trig40/conf30 | HYPE | 10 | −$790 | −3.08 |
| trig40/conf35 | BTC | 15 | −$197 | −0.33 |
| trig40/conf35 | ETH | 20 | −$472 | −0.96 |
| trig40/conf35 | HYPE | 22 | −$112 | −0.15 |

## One-line verdicts

- **Sparsity dominates everything.** Even the loosest variant
  (trig40/conf35) manages only 15–22 trades per coin over seven
  months. With n this small, every cell's sign is noise — the
  trig35/conf35 BTC print (+$644, Sharpe 1.43, n=7) is a lottery
  ticket, not a finding.
- **Loosening helps participation, not edge:** trig40 roughly doubles
  trade count but every coin stays negative. More trades of the same
  structurally-late entry just lose more slowly.
- **The real problem is the lag, not the levels:** the 5-bar pivot
  confirmation means the RSI re-cross usually fires *during* the
  confirmation window, before the setup is even "known". No level
  tweak fixes a same-bar problem with a lagged design.
- **Verdict:** shipped config (trig35/conf30, the documented
  classical rules) stands. No variant promoted. The honest next step
  is not another parameter — it is a redesign where divergence and
  confirmation are evaluated on the same bar, or dropping the
  re-cross requirement entirely in favor of entering at the second
  pivot extreme.
