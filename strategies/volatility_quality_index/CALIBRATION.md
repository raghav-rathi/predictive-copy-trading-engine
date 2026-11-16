# Volatility Quality Index — Calibration

Gate sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 1.5xATR
stop, 2R target, 48-bar max hold). The sweep re-runs
`add_indicators(df, gate_mult=g)` only — signals and risk are
unchanged. The gate is |10-bar VQI change| >= g * median(|10-bar
VQI change|, 50); g=0.0 means no gate.

| Gate | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.0 (off) | BTC | 1,606 | 37.9% | -$9,434 | -6.71 | 0.71 | -$5.87 |
| 0.0 (off) | ETH | 1,649 | 39.4% | -$8,047 | -3.44 | 0.85 | -$4.88 |
| 0.0 (off) | HYPE | 1,544 | 40.9% | -$6,322 | -2.35 | 0.88 | -$4.09 |
| 0.5 (shipped) | BTC | 1,243 | 37.5% | -$8,865 | -5.73 | 0.72 | -$7.13 |
| 0.5 (shipped) | ETH | 1,278 | 39.2% | -$7,143 | -3.04 | 0.85 | -$5.59 |
| 0.5 (shipped) | HYPE | 1,221 | 41.2% | -$4,277 | -1.39 | 0.91 | -$3.50 |
| 1.0 | BTC | 885 | 39.0% | -$7,168 | -3.93 | 0.73 | -$8.10 |
| 1.0 | ETH | 896 | 39.3% | -$6,734 | -3.32 | 0.80 | -$7.52 |
| 1.0 | HYPE | 889 | 42.2% | -$1,668 | -0.43 | 0.96 | -$1.88 |

## One-line verdict

- **gate=0.0 (off):** 1,544–1,649 trades per coin, combined
  -$23,804. No gate at all is the worst — the VQI change flips sign
  nearly every bar and the strategy trades on almost all of them.
- **gate=1.0:** 885–896 trades per coin, combined -$15,571 — the
  least bad, and HYPE nearly breaks even (-$1,668, PF 0.96). A
  stricter gate helps only by trading less; win rates barely move
  (39–42% at every setting) and expectancy per trade actually gets
  worse on BTC/ETH, so the improvement is fewer bets, not better
  bets.
- **gate=0.5 (shipped):** combined -$20,285, between the two — the
  gate filters out about a quarter of the noise entries and the
  loss falls roughly in proportion to the trade count.
- **Shipped decision:** keep the specified gate=0.5x as the registry
  config regardless. It was fixed before any backtest was run; the
  in-sample ranking (gate=1.0 loses least) does not change that,
  and leaning toward 1.0 *because* it loses least would be
  in-sample selection on a window where no setting works. The honest
  read: the gate moves how often the strategy bleeds fees, not
  whether the VQI-change sign predicts anything — at every setting
  the win rate sits in the high 30s and the profit factor below 1.
