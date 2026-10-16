# Ultimate Oscillator — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). Two parameters: the
oversold-confirmation level for bullish divergence (25/30/35) and the
fractal pivot width (k=3 vs k=5). Throwaway sweep script:
`/tmp/batch7_calibrate.py` (results in `/tmp/batch7_calib.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped os30/k3 | BTC | 64 | −$1,897 | −1.78 |
| shipped os30/k3 | ETH | 65 | −$1,577 | −0.58 |
| shipped os30/k3 | HYPE | 60 | −$758 | −0.57 |
| os25/k3 | BTC | 62 | −$1,719 | −1.58 |
| os25/k3 | ETH | 64 | −$1,486 | −0.50 |
| os25/k3 | HYPE | 58 | −$557 | −0.40 |
| os25/k5 | BTC | 54 | −$2,215 | −2.16 |
| os25/k5 | ETH | 54 | −$1,767 | −0.88 |
| os25/k5 | HYPE | 43 | −$1,148 | −1.32 |
| os30/k5 | BTC | 55 | −$2,299 | −2.26 |
| os30/k5 | ETH | 55 | −$1,855 | −0.95 |
| os30/k5 | HYPE | 47 | −$853 | −0.87 |
| os35/k3 | BTC | 65 | −$1,618 | −1.46 |
| os35/k3 | ETH | 70 | −$1,848 | −0.80 |
| os35/k3 | HYPE | 65 | −$1,353 | −1.09 |
| os35/k5 | BTC | 57 | −$1,778 | −1.62 |
| os35/k5 | ETH | 62 | −$2,242 | −1.28 |
| os35/k5 | HYPE | 54 | −$1,789 | −1.91 |

## One-line verdicts

- **Nothing helps.** Every variant loses on every coin. The least-bad
  cells (os25/k3 on HYPE, −$557) are still negative; the differences
  between variants are noise around a negative mean.
- **k=5 pivots lose more, not less:** fewer, "cleaner" pivots cut
  trades ~15% but the remaining divergences are no better — the
  problem is the premise (hourly divergence = pause, not reversal),
  not pivot quality.
- **Loosening the confirmation (os35) just adds losing trades:**
  more entries, worse combined result. Tightening (os25) trims losses
  slightly by trading less, which is the backtest telling you the
  kindest thing it can.
- **Verdict:** shipped config (os30/k3, the documented Williams
  rules) stands; no variant promoted. This strategy's value in the
  library is as a documented negative result, not a live candidate.
