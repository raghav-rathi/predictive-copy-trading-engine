# OBV Divergence — Calibration

Pivot-lag sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 1.5xATR stop,
2.5xATR trail, 60-bar max hold). The lag k is the confirmation window
for pivots: k=6 confirms faster (more, noisier pivots), k=14 confirms
slower (fewer, higher-quality pivots). The sweep re-runs
`add_indicators(df, pivot_k=X)` only — signals and risk are unchanged.

| Lag k | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 6 | BTC | 29 | 24.1% | -$1,187 | -2.82 | 0.23 | -$40.94 |
| 6 | ETH | 34 | 29.4% | -$427 | -0.67 | 0.75 | -$12.56 |
| 6 | HYPE | 25 | 28.0% | +$1,068 | +1.10 | 1.58 | +$42.71 |
| 10 (shipped) | BTC | 14 | 35.7% | -$275 | -0.92 | 0.60 | -$19.61 |
| 10 (shipped) | ETH | 20 | 30.0% | -$276 | -0.64 | 0.66 | -$13.81 |
| 10 (shipped) | HYPE | 15 | 26.7% | -$1 | +0.20 | 1.00 | -$0.04 |
| 14 | BTC | 13 | 46.2% | +$645 | +1.33 | 1.77 | +$49.60 |
| 14 | ETH | 19 | 36.8% | -$116 | -0.19 | 0.89 | -$6.08 |
| 14 | HYPE | 12 | 58.3% | +$213 | +0.57 | 1.60 | +$17.76 |

## One-line verdict

- **k=6:** worst on BTC (-$1,187, PF 0.23 — fast pivots churn into
  chop) but best on HYPE (+$1,068, Sharpe +1.10, PF 1.58) — combined
  -$546. HYPE's faster structure rewards the shorter lag.
- **k=10:** negative everywhere combined (-$551). The a-priori shipped
  setting.
- **k=14:** best combined (+$742) and the only lag positive on two of
  three coins (BTC +$645, HYPE +$213) — but 12–19 trades per coin is
  in-sample-luck territory, not evidence.
- **Shipped decision:** keep the specified k=10 as the registry config
  regardless. It was fixed before any backtest was run; the k=14
  combined win is an in-sample observation on a 44-trade sample and
  adopting it *because* of that would be in-sample selection. The
  honest read: the lag is a real sensitivity knob (slower = fewer,
  better trades; faster = HYPE-only gains at BTC's expense), and the
  right choice needs out-of-sample evidence, not this window.
