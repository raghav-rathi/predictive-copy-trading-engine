# ADX Bollinger Squeeze — Calibration

ADX-threshold sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The ADX entry threshold is the
strategy's natural knob: how much trend strength the
breakout must show — 15 admits more breakouts, 25 admits
only the strongest. The sweep re-runs `add_signals(df,
adx_entry=X)` only — indicators and risk are unchanged.
The ADX exit threshold stays 15 throughout.

| ADX entry | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 15 | BTC | 82 | 29.3% | -$11 | +0.04 | 0.99 | -$0.14 |
| 15 | ETH | 81 | 34.6% | +$913 | +1.30 | 1.54 | +$11.27 |
| 15 | HYPE | 109 | 32.1% | +$63 | +0.16 | 1.03 | +$0.58 |
| 20 (shipped) | BTC | 65 | 27.7% | +$63 | +0.14 | 1.04 | +$0.97 |
| 20 (shipped) | ETH | 60 | 35.0% | +$820 | +1.38 | 1.71 | +$13.66 |
| 20 (shipped) | HYPE | 69 | 29.0% | -$212 | -0.51 | 0.87 | -$3.08 |
| 25 | BTC | 46 | 32.6% | +$544 | +0.76 | 1.44 | +$11.83 |
| 25 | ETH | 48 | 35.4% | +$705 | +1.41 | 1.83 | +$14.68 |
| 25 | HYPE | 50 | 28.0% | -$159 | -0.47 | 0.87 | -$3.18 |

## One-line verdict

- **15:** combined +$965 on 272 trades — more trades, more
  fees ($2,189), best on ETH (+$913) and the only HYPE
  reading above water (+$63), but BTC goes negative (-$11).
- **20:** the shipped setting — combined +$670 on 194
  trades; the best ETH read (+$820, PF 1.71) sits here, the
  worst HYPE read (-$212) too.
- **25:** the best combined read (+$1,090, 144 trades) —
  best on BTC (+$544, PF 1.44) and fewest trades/fees
  ($1,155), but HYPE stays negative (-$159) and ETH is
  slightly worse than at 20 (+$705 vs +$820).
- **Shipped decision:** keep the specified ADX entry = 20
  as the registry config regardless. It was fixed before
  any backtest was run; adopting 25 *because* it is the
  best combined in-sample would be in-sample selection on
  a knob whose effect is not monotone across coins (25 wins
  BTC, loses ETH vs 20, and HYPE is negative at every
  setting). All three settings are positive combined, which
  says the squeeze + ADX idea is not obviously threshold-
  fragile — but that is a diagnostic observation, not a
  reason to move the knob. Do not ship 25 on the strength
  of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Bollinger Bands
  and ADX(14) are causal rolling/Wilder computations; the
  squeeze compares bandwidth against its own trailing
  20-bar minimum; signals use `crossed_above` /
  `crossed_below` on bars i and i−1 plus the trailing
  3-bar squeeze window (shifts of 1–2 bars, never forward);
  no `ichimoku` chikou column is used anywhere. The
  truncation test (`test_no_lookahead_truncation`) confirms
  indicator and signal values at bar j are identical
  whether computed on the full frame or on the frame
  truncated at j.
- **Source check:** the Bandwidth formula (upper − lower) /
  mid and the squeeze as a low-Bandwidth setup are
  confirmed by the cited Nasdaq explainer (verified via
  web search 2026-11-25). The 20-bar-minimum squeeze
  definition and the 3-bar lookback are this strategy's
  own parameterisation, stated as such in the README.
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.adx_bollinger_squeeze.test_adx_bollinger_squeeze`).
- **No parameter was tuned to PnL.** ADX entry stays 20.
