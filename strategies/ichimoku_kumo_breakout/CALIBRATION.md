# Ichimoku Kumo Breakout — Calibration

Senkou-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The senkou period is the strategy's
natural knob: how far back Senkou B looks — 26 makes a
narrower, faster cloud (more breakouts), 78 makes a wider,
slower one (fewer breakouts, later). The sweep re-runs
`add_indicators(df, senkou=X)` only — signals and risk are
unchanged. Tenkan 9 / kijun 26 are held at the Hosoda
standard throughout.

| Senkou | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 26 | BTC | 186 | 22.0% | -$3,198 | -2.77 | 0.57 | -$17.19 |
| 26 | ETH | 188 | 27.1% | -$1,347 | -0.86 | 0.82 | -$7.17 |
| 26 | HYPE | 190 | 26.3% | +$839 | +0.87 | 1.11 | +$4.42 |
| 52 (shipped) | BTC | 181 | 21.5% | -$2,851 | -2.51 | 0.60 | -$15.75 |
| 52 (shipped) | ETH | 176 | 24.4% | -$2,983 | -2.66 | 0.59 | -$16.95 |
| 52 (shipped) | HYPE | 183 | 24.6% | -$1,012 | -0.58 | 0.85 | -$5.53 |
| 78 | BTC | 192 | 20.3% | -$3,398 | -3.05 | 0.53 | -$17.70 |
| 78 | ETH | 189 | 21.2% | -$3,200 | -3.02 | 0.53 | -$16.93 |
| 78 | HYPE | 179 | 25.7% | +$115 | +0.35 | 1.02 | +$0.65 |

## One-line verdict

- **26:** the least bad combined read (-$3,707, 564 trades)
  and the best single-coin cell in the whole batch (HYPE
  +$839, Sharpe +0.87, PF 1.11) — but BTC (-$3,198, the
  worst BTC cell in the sweep) and ETH (-$1,347) still
  lose, so the "improvement" is one coin, not a system.
- **52:** the shipped setting — combined -$6,846, 540
  trades, PF 0.68. The worst combined read of the three
  values, and the worst loser of this batch's three
  strategies.
- **78:** near-identical to 52 combined (-$6,483, 560
  trades) — BTC and ETH both worse than at 52 (-$3,398 /
  -$3,200, Sharpe ≈ -3.0), HYPE slightly positive (+$115).
  A slower cloud does not help; it just delays the same
  losing breakouts.
- **Shipped decision:** keep the specified senkou period 52
  as the registry config regardless. It was fixed before any
  backtest was run; adopting 26 *because* it is least bad
  in-sample would be in-sample selection on a knob whose
  effect is not even monotone by coin (26 wins HYPE by a
  mile and loses BTC badly; 78 wins HYPE slightly and loses
  BTC/ETH worst). The honest read: the shipped 52-period
  cloud is structurally too slow for 1h crypto, and the
  sweep shows the "right" width is not identifiable from
  this window. Do not ship 26 on the strength of this sweep.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. Tenkan/kijun are
  rolling extremes through bar j; senkou A/B are those
  values shifted +26, so the cloud read at bar j was
  computed from data through bar j−26. The chikou column
  (close shifted −26, a lookahead) is never copied into the
  frame — `test_chikou_never_copied` asserts its absence.
  Signals use `crossed_above`/`crossed_below` on bars i and
  i−1 only, plus the current bar's tenkan/kijun comparison
  and cloud-edge level exits. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the Wikipedia "Ichimoku Kinkō Hyō"
  article (verified via search 2026-11-25) confirms Hosoda
  as the developer, tenkan (9) / kijun (26) / senkou A and
  B (52, plotted 26 ahead) formulas, the Kumo as the space
  between the senkou spans, and chikou as today's close
  projected back 26 periods. The implementation matches:
  `test_senkou_spans_are_shifted_26` verifies the +26 shift
  numerically. No bug found.
- **Tests:** 13/13 pass (`python3 -m unittest
  strategies.ichimoku_kumo_breakout.test_ichimoku_kumo_breakout`).
- **No parameter was tuned to PnL.** Senkou period stays 52.
