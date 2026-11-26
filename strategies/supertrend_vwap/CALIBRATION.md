# Supertrend VWAP — Calibration

Supertrend-multiplier sensitivity on the same Hyperliquid 1h
data as BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The multiplier is the strategy's
natural knob: 2.0 is the tighter/faster line, 3.0 the
standard, 4.0 the looser/slower one. The sweep re-runs
`add_indicators(df, st_k=X)` — the ATR period stays 10 and
the session-VWAP construction is unchanged throughout.

| ST multiplier | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2.0 | BTC | 872 | 22.0% | -$8,707 | -7.90 | 0.48 | -$9.98 |
| 2.0 | ETH | 894 | 22.4% | -$8,312 | -6.41 | 0.53 | -$9.30 |
| 2.0 | HYPE | 808 | 25.9% | -$6,049 | -4.00 | 0.69 | -$7.49 |
| 3.0 (shipped) | BTC | 818 | 19.9% | -$8,694 | -8.23 | 0.45 | -$10.63 |
| 3.0 (shipped) | ETH | 847 | 22.1% | -$8,510 | -7.16 | 0.49 | -$10.05 |
| 3.0 (shipped) | HYPE | 754 | 25.7% | -$5,908 | -4.15 | 0.66 | -$7.84 |
| 4.0 | BTC | 771 | 20.4% | -$8,379 | -7.73 | 0.46 | -$10.87 |
| 4.0 | ETH | 804 | 21.4% | -$8,250 | -6.96 | 0.49 | -$10.26 |
| 4.0 | HYPE | 712 | 26.0% | -$4,838 | -3.04 | 0.72 | -$6.80 |

## One-line verdict

- **2.0:** combined -$23,068 on 2,574 trades — the most
  trades, the most fees ($10,191), and no better than
  shipped.
- **3.0:** the shipped setting — combined -$23,112 on 2,419
  trades; the worst combined read in the sweep by $44.
- **4.0:** combined -$21,468 on 2,287 trades — the "least
  bad" read, but the improvement is $1,644 on a $23k loss
  with win% and PF essentially unchanged (22.5% / 0.46–0.72);
  the multiplier moves the loss by ~7%, not the sign.
- **Shipped decision:** keep the specified Supertrend
  multiplier = 3.0 as the registry config regardless. It was
  fixed before any backtest was run; the sweep is diagnostic
  only. All three settings lose $21–23k on all three coins,
  so the knob is irrelevant — the agreement logic itself
  loses, and no multiplier in this sweep is worth switching
  to. Do not ship a different multiplier on the strength of
  this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The Supertrend
  ratchet uses only closes through bar i; the session VWAP
  is a causal cumulative sum resetting at 00:00 UTC; signals
  read bar-i values at bar i; no `ichimoku` chikou column is
  used anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j — including
  the VWAP, whose day-grouped cumsum is unchanged by
  truncation within the day.
- **Source check:** the Supertrend construction (ATR bands
  around the bar midpoint, one-way ratchet, standard defaults
  ATR 10 / multiplier 3, Olivier Seban) is confirmed by the
  cited Investopedia page (verified via web search
  2026-11-26). The session VWAP follows the sibling
  vwap_session_breakout UTC-day anchor exactly (via
  base.anchored_vwap).
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.supertrend_vwap.test_supertrend_vwap`).
- **No parameter was tuned to PnL.** Supertrend multiplier stays 3.0.
