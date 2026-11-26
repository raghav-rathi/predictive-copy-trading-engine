# Heikin Ashi ADX — Calibration

ADX-entry-threshold sensitivity on the same Hyperliquid 1h
data as BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The ADX entry threshold is the
strategy's natural knob: 20 is the looser trend gate, 25 the
standard, 30 the stricter one. The sweep re-runs
`add_signals(df, adx_entry=X)` — the ADX exit threshold
stays 20 and the HA construction is unchanged throughout.

| ADX entry | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 20 | BTC | 788 | 22.1% | -$8,492 | -9.15 | 0.39 | -$10.78 |
| 20 | ETH | 792 | 26.0% | -$7,239 | -5.91 | 0.55 | -$9.14 |
| 20 | HYPE | 737 | 28.9% | -$6,112 | -4.95 | 0.60 | -$8.29 |
| 25 (shipped) | BTC | 565 | 20.0% | -$7,277 | -7.45 | 0.41 | -$12.88 |
| 25 (shipped) | ETH | 562 | 26.3% | -$6,063 | -4.99 | 0.53 | -$10.79 |
| 25 (shipped) | HYPE | 497 | 27.4% | -$4,622 | -4.08 | 0.60 | -$9.30 |
| 30 | BTC | 367 | 20.4% | -$5,843 | -6.04 | 0.37 | -$15.92 |
| 30 | ETH | 393 | 25.7% | -$4,780 | -4.22 | 0.52 | -$12.16 |
| 30 | HYPE | 326 | 27.3% | -$3,541 | -3.40 | 0.59 | -$10.86 |

## One-line verdict

- **20:** combined -$21,843 on 2,317 trades — the loosest
  gate trades the most and pays the most fees ($9,482); the
  worst combined read in the sweep.
- **25:** the shipped setting — combined -$17,962 on 1,624
  trades; still a catastrophic loser on every coin.
- **30:** combined -$14,164 on 1,086 trades — the "least
  bad" read, but only because it trades less: per-trade
  expectancy is the worst of the three settings on every coin
  (BTC -$15.92 vs -$12.88 shipped), and PF is flat-to-worse
  (0.37–0.59). The threshold does not create an edge; it
  rations a losing system.
- **Shipped decision:** keep the specified ADX entry
  threshold = 25 as the registry config regardless. It was
  fixed before any backtest was run; the sweep is diagnostic
  only. All three settings lose heavily on all three coins,
  so there is no setting in this sweep worth switching to —
  the knob is not stable, it just trades a loser more or
  less often. Do not ship a different threshold on the
  strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The HA recursion
  uses only the current and previous bars; ADX/+DI/−DI are
  Wilder smoothing; signals read bar-i values at bar i; no
  `ichimoku` chikou column is used anywhere. The truncation
  test (`test_no_lookahead_truncation`) confirms indicator
  and signal values at bar j are identical whether computed
  on the full frame or on the frame truncated at j.
- **Source check:** the HA construction (average close,
  midpoint open, max/min envelope) is confirmed by the cited
  Wikipedia page (verified via web search 2026-11-26).
  One documented deviation: none — the implementation follows
  the sibling heikin_ashi_trend HA recursion exactly,
  including seeding ha_open[0] with the first real open.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.heikin_ashi_adx.test_heikin_ashi_adx`).
- **No parameter was tuned to PnL.** ADX entry stays 25.
