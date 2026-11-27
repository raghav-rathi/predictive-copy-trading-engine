# ATR Expansion Breakout (NR7) — Calibration

Bracket-validity and NR-window sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-48 window 2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC,
6,184 bars BTC/ETH, 6,182 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 48-bar max hold). The sweeps re-run
`add_indicators(df, validity_bars=X)` / `add_indicators(df,
nr_n=X)` -- everything else stays fixed.

## Bracket validity (NR window fixed at 7)

| Validity | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2 bars | BTC | 534 | 24.2% | -$6,505 | -5.08 | 0.56 | -$12.18 |
| 2 bars | ETH | 502 | 27.3% | -$5,042 | -3.36 | 0.67 | -$10.04 |
| 2 bars | HYPE | 520 | 31.2% | -$4,186 | -2.66 | 0.75 | -$8.05 |
| 2 bars | **Combined** | **1,556** | **27.5%** | **-$15,734** | — | **0.66** | — |
| 3 bars (shipped) | BTC | 582 | 24.9% | -$6,589 | -4.95 | 0.59 | -$11.32 |
| 3 bars (shipped) | ETH | 565 | 27.3% | -$5,769 | -3.99 | 0.64 | -$10.21 |
| 3 bars (shipped) | HYPE | 587 | 31.0% | -$5,001 | -3.32 | 0.72 | -$8.52 |
| 3 bars (shipped) | **Combined** | **1,734** | **27.7%** | **-$17,359** | **-5.85** | **0.65** | **-$10.01** |
| 5 bars | BTC | 662 | 25.8% | -$6,438 | -4.41 | 0.64 | -$9.72 |
| 5 bars | ETH | 648 | 27.8% | -$6,042 | -3.98 | 0.66 | -$9.32 |
| 5 bars | HYPE | 671 | 30.4% | -$5,477 | -3.62 | 0.71 | -$8.16 |
| 5 bars | **Combined** | **1,981** | **28.0%** | **-$17,957** | — | **0.67** | — |

## NR window (validity fixed at 3 bars)

| NR window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| NR4 | BTC | 824 | 26.2% | -$7,911 | -6.63 | 0.56 | -$9.60 |
| NR4 | ETH | 781 | 28.4% | -$5,794 | -3.44 | 0.70 | -$7.42 |
| NR4 | HYPE | 780 | 32.2% | -$5,027 | -3.00 | 0.76 | -$6.45 |
| NR4 | **Combined** | **2,385** | **28.9%** | **-$18,732** | — | **0.68** | — |
| NR7 (shipped) | **Combined** | **1,734** | **27.7%** | **-$17,359** | **-5.85** | **0.65** | **-$10.01** |

## One-line verdict

- **Validity 2:** combined -$15,734 on 1,556 trades -- the
  least-bad variant, still a large loser; fewer trades, same
  failure mode.
- **Validity 3:** the shipped setting -- combined -$17,359
  on 1,734 trades.
- **Validity 5:** combined -$17,957 on 1,981 trades -- a
  longer window just admits more failed breakouts.
- **NR4:** combined -$18,732 on 2,385 trades -- the looser
  narrow-range definition churns even harder.
- **Shipped decision:** keep NR window = 7 and bracket
  validity = 3 bars as the registry config regardless. Both
  were fixed before any backtest was run; the sweeps are
  diagnostic only. No swept variant is profitable, so there
  is nothing to tune toward -- the edge is absent, not
  mis-parameterized. Do not ship a different validity or
  window on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The NR7 test
  compares the current bar's range only against the six
  preceding bars; ATR(14) is Wilder smoothing; the bracket
  state machine only reads bars up to the current one;
  entries are crossed_above / crossed_below on the armed
  levels. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the NR7 construction (narrowest range of
  7, bracket = NR7 high/low, trade the breakout within the
  next few bars) matches the cited Crabel references. Two
  documented choices: bracket validity fixed at 3 bars (the
  sources do not fix a number) and the both-triggers-same-bar
  enter-neither guard (intrabar order is unknowable from
  OHLC data).
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.atr_expansion_breakout.test_atr_expansion_breakout`).
- **No parameter was tuned to PnL.** NR window stays 7,
  validity stays 3.
