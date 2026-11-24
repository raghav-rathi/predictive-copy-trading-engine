# Spinning Top — Calibration

Swing-lookback sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, batch-45 window 2026-03-14 →
2026-11-24, ms `[1773525600000, 1795525200000)`, same
costs/sizing, 2xATR stop, 3xATR trail, 60-bar max hold). The
lookback is the strategy's natural knob: how far back the
"swing extreme" reaches — 10 is a local extreme (more setups),
40 a major one (fewer setups). The sweep re-runs
`add_indicators(df, swing_lookback=X)` only — signals and
risk are unchanged. Re-run on the batch-45 window with the
pinned runner's loader (local cache only); the Nov-14 sweep
numbers were superseded and are not retained here.

| swing | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 143 | 31.47% | -$2,102.20 | -1.56 | 0.74 | -$14.70 |
| 10 | ETH | 121 | 46.28% | +$1,072.84 | +0.89 | 1.18 | +$8.87 |
| 10 | HYPE | 170 | 32.35% | -$2,698.49 | -2.07 | 0.68 | -$15.87 |
| 20 (shipped) | BTC | 97 | 29.90% | -$1,518.79 | -1.41 | 0.74 | -$15.66 |
| 20 (shipped) | ETH | 72 | 34.72% | -$788.83 | -0.76 | 0.80 | -$10.96 |
| 20 (shipped) | HYPE | 123 | 30.08% | -$1,741.50 | -1.33 | 0.74 | -$14.16 |
| 40 | BTC | 64 | 25.00% | -$1,443.44 | -1.62 | 0.65 | -$22.55 |
| 40 | ETH | 43 | 30.23% | -$867.64 | -1.20 | 0.65 | -$20.18 |
| 40 | HYPE | 81 | 32.10% | -$114.58 | -0.01 | 0.98 | -$1.41 |

## One-line verdict

- **10:** loosest extreme, most trades (434) — combined
  -$3,727.85 and worst on BTC (-$2,102.20) and HYPE
  (-$2,698.49), but the only positive ETH read (+$1,072.84,
  win rate 46.28%). One coin does not rescue a system.
- **40:** strictest extreme, fewest trades (188) — least-bad
  combined (-$2,425.66) and best on BTC and HYPE (HYPE -$114.58,
  PF 0.98), but worst per-trade expectancy on BTC (-$22.55).
  Fewer, more "significant" extremes still lose.
- **20:** middle ground (-$4,049.12 combined) — worst combined
  of the three, and best on no coin.
- **Shipped decision:** keep the specified swing_lookback=20
  as the registry config regardless. It was fixed before any
  backtest was run; adopting 40 *because* it is least-bad
  in-sample would still be in-sample selection. The honest
  read: the knob is nearly flat in the wrong place (combined
  net spans -$2,425.66 to -$4,049.12, all negative, PF ≤ 0.80
  on every coin at the shipped setting) — the problem is not
  how far back the extreme reaches, it is that a spinning top
  at an extreme does not reverse a 1h crypto trend.
