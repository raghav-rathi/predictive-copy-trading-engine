# Donchian Stochastic — Calibration

Entry-window sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The entry channel window is the
strategy's natural knob: 10 bars is the faster Turtle
system, 20 the standard, 55 the slower Turtle system. The
sweep re-runs `add_indicators(df, entry_n=X)` and
`add_signals(df, entry_n=X)` — the exit channel stays 10
bars and the Stochastic filter stays 80/20 throughout.

| Entry window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 70 | 24.3% | -$1,768 | -4.94 | 0.22 | -$25.26 |
| 10 | ETH | 85 | 34.1% | -$923 | -2.02 | 0.55 | -$10.86 |
| 10 | HYPE | 56 | 37.5% | -$52 | -0.12 | 0.96 | -$0.93 |
| 20 (shipped) | BTC | 22 | 13.6% | -$61 | -0.07 | 0.93 | -$2.80 |
| 20 (shipped) | ETH | 31 | 35.5% | -$175 | -0.66 | 0.68 | -$5.66 |
| 20 (shipped) | HYPE | 8 | 25.0% | +$405 | +2.06 | 3.65 | +$50.57 |
| 55 | BTC | 6 | 33.3% | -$67 | -0.62 | 0.58 | -$11.24 |
| 55 | ETH | 13 | 46.2% | +$84 | +0.41 | 1.36 | +$6.44 |
| 55 | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |

## One-line verdict

- **10:** combined -$2,743 on 211 trades — the fastest
  channel trades the most and loses on every coin (BTC PF
  0.22, expectancy -$25.26); the filter cannot save the
  fast channel.
- **20:** the shipped setting — the only clearly positive
  combined read (+$168, 61 trades), but it rests entirely
  on HYPE's 8 trades (+$405) while BTC and ETH both lose;
  the "win" is an 8-trade sample.
- **55:** combined +$16 on 19 trades — positive by $16 and
  meaningless: HYPE trades zero times (the 55-bar channel
  plus the %K filter never fires there), and ETH's +$84 on
  13 trades is noise.
- **Shipped decision:** keep the specified entry window =
  20 as the registry config regardless. It was fixed before
  any backtest was run; the sweep is diagnostic only. The
  20-bar window being the only positive combined read is
  in-sample information on a 61-trade sample, and the 10-
  and 55-bar reads bracket it with a $2,743 loss and a $16
  wash — the knob is not stable, it is just the middle of
  three marginal settings. Do not ship a different window on
  the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Donchian
  channels are causal rolling extremes; %K/%D are causal
  rolling extremes plus a causal SMA; signals compare the
  close against the channels shifted by 1 (prior bars only);
  no `ichimoku` chikou column is used anywhere. The
  truncation test (`test_no_lookahead_truncation`) confirms
  indicator and signal values at bar j are identical whether
  computed on the full frame or on the frame truncated at j.
- **Source check:** the channel construction (highest high
  / lowest low of the last N periods, N usually 20) and the
  long-above / short-below rule are confirmed by the cited
  Donchian Wikipedia page; the %K/%D construction and 80/20
  levels are confirmed by the cited Stochastic oscillator
  Wikipedia page (both verified via web search 2026-11-26).
  One documented deviation: the 10-bar Turtle exit is judged
  against the prior bars' channel (shifted by 1), because
  the unshifted 10-bar low includes the current bar's own
  low and the close can never be below it — the unshifted
  reading could never fire. A second documented property,
  not a deviation: on tight-spread synthetic data the %K
  filter blocks nearly every breakout (a breakout close sits
  at the range extreme, so %K ≈ 100/0); the filter only
  passes on wicky breakout bars, which is why the system
  trades 61 times where the RSI-filtered Donchian combo
  trades 536.
- **Tests:** 19/19 pass (`python3 -m unittest
  strategies.donchian_stochastic.test_donchian_stochastic`).
- **No parameter was tuned to PnL.** Entry window stays 20.
