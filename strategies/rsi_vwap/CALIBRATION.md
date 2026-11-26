# RSI + Session VWAP — Calibration

RSI-level sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The RSI oversold/overbought levels
are the strategy's natural knob: 20/80 is the stricter
extreme-only setting, 30/70 the shipped standard, 40/60 the
looser setting (entries fire far more often). The sweep
re-runs `add_signals(df, rsi_oversold=X, rsi_overbought=Y)`
-- the RSI period stays 14, the exit midline stays 50, and
the VWAP side is unchanged throughout.

| RSI levels | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 20/80 | BTC | 7 | 14.3% | -$67 | -0.39 | 0.61 | -$9.50 |
| 20/80 | ETH | 10 | 10.0% | -$343 | -2.83 | 0.03 | -$34.31 |
| 20/80 | HYPE | 7 | 14.3% | -$118 | -0.86 | 0.44 | -$16.81 |
| 30/70 (shipped) | BTC | 51 | 25.5% | -$642 | -1.26 | 0.60 | -$12.58 |
| 30/70 (shipped) | ETH | 41 | 24.4% | -$343 | -0.71 | 0.70 | -$8.36 |
| 30/70 (shipped) | HYPE | 36 | 27.8% | +$638 | +1.33 | 1.53 | +$17.71 |
| 40/60 | BTC | 217 | 25.8% | -$3,941 | -4.91 | 0.39 | -$18.16 |
| 40/60 | ETH | 200 | 31.5% | -$1,530 | -1.58 | 0.69 | -$7.65 |
| 40/60 | HYPE | 227 | 25.1% | -$1,122 | -1.25 | 0.81 | -$4.94 |

## One-line verdict

- **20/80:** combined -$527 on 24 trades -- negative on
  every coin (PF 0.03-0.61); the strictest levels trade the
  least and still lose, with ETH the worst (1 win in 10).
- **30/70:** the shipped setting -- combined -$347 on 128
  trades; the least-bad combined read, entirely because
  HYPE (+$638) offsets BTC and ETH.
- **40/60:** combined -$6,593 on 644 trades -- negative on
  every coin by a wide margin; the looser levels quintuple
  the trade count and pay $4,154 in fees for the privilege
  (expectancy -$5 to -$18 per trade).
- **Shipped decision:** keep the specified RSI levels =
  30/70 as the registry config regardless. They were fixed
  before any backtest was run; the sweep is diagnostic only.
  The 30/70 read being the least-bad of three losing
  settings is in-sample information, not evidence the
  levels have edge -- every setting loses combined, and the
  40/60 blowout shows the knob is unstable in the loss
  direction. Do not ship different levels on the strength
  of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Session VWAP is
  causal cumulative sums through the current bar's close
  (reset at each UTC-day boundary); RSI(14) is Wilder
  smoothing; entries compare the close against the current
  bar's VWAP (both known at the close) and RSI crosses
  against the prior bar's values; no `ichimoku` chikou
  column is used anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the RSI construction (Wilder RSI(14),
  30/70 oversold/overbought, 50 midline) matches the cited
  reference, and the session-VWAP construction matches
  `vwap_session_breakout` exactly (verified against its
  indicators.py: same typical-price, volume-weighted,
  UTC-day cumulative-sum form).
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.rsi_vwap.test_rsi_vwap`).
- **No parameter was tuned to PnL.** RSI levels stay 30/70.
