# Popgun Bar Pattern — Calibration

Bracket-validity sensitivity on the same Hyperliquid 1h
data as BACKTEST.md (BTC/ETH/HYPE, pinned batch-49 window
2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC, 6,185 bars
BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 48-bar max hold). The sweeps re-run
`add_indicators(df, validity_bars=X)` -- everything else
stays fixed.

## Bracket validity

| Validity | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 3 bars | BTC | 118 | 30.5% | -$1,594 | -1.28 | 0.72 | -$13.51 |
| 3 bars | ETH | 111 | 32.4% | -$664 | -0.37 | 0.87 | -$5.98 |
| 3 bars | HYPE | 126 | 27.8% | -$1,373 | -0.96 | 0.79 | -$10.90 |
| 3 bars | **Combined** | **355** | **30.1%** | **-$3,631** | — | **0.79** | — |
| 5 bars (shipped) | BTC | 147 | 32.0% | -$1,157 | -0.67 | 0.83 | -$7.87 |
| 5 bars (shipped) | ETH | 133 | 33.1% | -$1,080 | -0.70 | 0.83 | -$8.12 |
| 5 bars (shipped) | HYPE | 145 | 29.7% | -$1,220 | -0.79 | 0.83 | -$8.41 |
| 5 bars (shipped) | **Combined** | **425** | **31.5%** | **-$3,457** | **-1.17** | **0.83** | **-$8.13** |
| 8 bars | BTC | 177 | 30.5% | -$1,815 | -1.09 | 0.78 | -$10.25 |
| 8 bars | ETH | 168 | 31.5% | -$1,374 | -0.82 | 0.83 | -$8.18 |
| 8 bars | HYPE | 174 | 31.0% | +$113 | 0.18 | 1.01 | +$0.65 |
| 8 bars | **Combined** | **519** | **31.0%** | **-$3,076** | — | **0.88** | — |

## One-line verdict

- **Validity 3:** combined -$3,631 on 355 trades -- fewer
  trades, same failure mode, worst BTC (-$1,594).
- **Validity 5:** the shipped setting -- combined -$3,457
  on 425 trades.
- **Validity 8:** combined -$3,076 on 519 trades -- the
  least-bad variant, still a loser. Its only bright spot is
  HYPE at +$113 on 174 trades (PF 1.01, Sharpe 0.18), which
  is a wobble around zero on one coin, not an edge: BTC
  and ETH both get worse than at validity 5, and the
  combined number stays negative with higher fees ($3,937).
- **Shipped decision:** keep bracket validity = 5 bars as
  the registry config regardless. It was fixed before any
  backtest was run; the sweeps are diagnostic only. No swept
  variant is profitable combined, so there is nothing to
  tune toward -- the edge is absent, not mis-parameterized.
  Do not ship validity 8 on the strength of the HYPE
  number.

## Audit

- **Lookahead audit:** no lookahead found. The inside /
  outside tests compare the current bar only against the
  preceding bar; the bracket state machine only reads bars
  up to the current one; entries are crossed_above /
  crossed_below on the armed levels. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the popgun construction (inside bar
  followed by an engulfing outside bar, bracket = the
  outside bar's high/low, trade the breakout) matches the
  cited Kennedy reference. Two documented choices: bracket
  validity fixed at 5 bars (the source does not fix a
  number) and the both-triggers-same-bar enter-neither guard
  (intrabar order is unknowable from OHLC data).
- **Tests:** 18/18 pass (`python3 -m unittest
  strategies.popgun.test_popgun`).
- **No parameter was tuned to PnL.** Validity stays 5.
