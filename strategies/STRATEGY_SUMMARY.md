# Strategy Library — Empirical Summary (2026-10-09)

12 technical strategies, each: indicators + signals + risk config + unit
tests (87 green) + backtest on real Hyperliquid 1h candles
(2026-03-14 → 2026-10-09, ~5,000 bars/coin). Costs: 0.045% taker +
0.01% slippage/side. Sizing: 1% equity risk/trade, 3x leverage cap, $10k.

Net return % by coin (Sharpe in parens):

| Strategy | BTC | ETH | HYPE | Verdict |
|---|---|---|---|---|
| donchian (480/240) | +4.4 (0.74) | -5.7 (-0.92) | +4.6 (0.67) | mixed |
| supertrend | -21.0 (-3.11) | -13.2 (-1.63) | **+17.7 (1.90)** | regime-dependent |
| rsi2 | -15.2 (-2.06) | -14.6 (-1.98) | -6.3 (-0.89) | loser |
| bollinger_squeeze | +3.2 (0.36) | +3.0 (0.35) | -1.5 (-0.05) | small positive |
| macd_momentum | -24.6 (-2.34) | -16.8 (-1.28) | +7.0 (0.64) | regime-dependent |
| ichimoku | -3.6 (-0.43) | -2.3 (-0.26) | **+11.2 (1.54)** | regime-dependent |
| vwap_reversion | -64.1 (-5.64) | -40.0 (-2.68) | -58.0 (-5.13) | loser (killed) |
| keltner_adx | -15.4 (-1.57) | -6.3 (-0.56) | +1.8 (0.29) | loser |
| funding_tilt | +2.4 (0.43) | -9.6 (-1.14) | +0.1 (0.06) | mixed |
| williams_breakout | +7.3 (0.83) | +0.8 (0.17) | **+25.3 (3.28)** | small positive |
| ema_vwap_retest | -35.9 (-5.62) | -13.1 (-1.05) | -17.8 (-2.36) | loser (port failure) |
| opening_range_breakout | -62.3 (-3.92) | -19.9 (-0.68) | -17.3 (-0.59) | loser (port failure) |

## Read it straight

- **No strategy wins on all three coins.** The closest: williams_breakout
  and bollinger_squeeze are positive-or-flat everywhere, but thin.
- **HYPE was a parabolic alt in 2026** — trend systems (supertrend,
  ichimoku, macd, williams) print on HYPE and bleed on choppy BTC/ETH.
  That's regime, not alpha. Any "winner" must survive BTC/ETH chop too.
- **1h breakout systems die in chop**: donchian-20, supertrend, keltner —
  all negative on BTC/ETH. The Donchian calibration proved the edge only
  exists at the daily scale (480/240 bars).
- **Mean-reversion dies in trends**: rsi2 and vwap_reversion fade moves
  that keep moving. VWAP reversion (-64%) is the worst in the library.
- **Port failures are honest failures**: ema_vwap_retest (10m equities →
  1h crypto) and opening_range_breakout (tick scalp → 1h bars) lose because
  the timeframe/market changed, not because the original systems are bad.
- **Lookahead almost shipped**: the first Ichimoku run showed +16%/+18%
  (Sharpe 2.3/2.7) from a Chikou implementation peeking 26 bars ahead.
  Caught, fixed, true result is a mild loser. Forward-shifted indicators
  are now a known trap in this codebase.

## What clears the bar for an ensemble sleeve

williams_breakout and bollinger_squeeze (positive-or-flat on all three,
right-shaped risk profiles). Everything else is research material until
it proves itself on more coins and longer windows. Nothing here is for
live capital as a standalone.

---

# Batch 2 — 2026-10-10 (10 new strategies, 60 commits)

10 classic published systems, each: indicators + signals + risk config +
unit tests (96 green across the batch) + backtest on real Hyperliquid 1h
candles (2026-03-14 → 2026-10-10, ~5,030 bars/coin). Costs: 0.045% taker +
0.01% slippage/side. Sizing: 1% equity risk/trade, 3x leverage cap, $10k.

Net return % by coin (Sharpe in parens):

| Strategy | BTC | ETH | HYPE | Verdict |
|---|---|---|---|---|
| dual_thrust (0.7/0.7) | +3.9 (0.91) | +10.3 (1.41) | +13.9 (2.03) | **WINNER** |
| chandelier_exit | -21.8 (-1.43) | -3.4 (-0.06) | +17.0 (1.06) | mixed |
| darvas_box | -11.7 (-1.68) | +27.1 (1.82) | +4.4 (0.49) | mixed |
| kama_trend | -21.6 (-3.06) | -6.6 (-0.82) | +8.9 (1.11) | mixed |
| awesome_oscillator | -0.6 (-0.08) | -15.3 (-0.57) | +1.6 (0.25) | mixed/leaning loser |
| parabolic_sar | -25.6 (-1.97) | -16.7 (-1.17) | +3.1 (0.35) | loser |
| connors_rsi | -13.4 (-3.76) | -12.5 (-2.88) | -10.8 (-2.78) | loser |
| gmma | -21.8 (-1.71) | -25.2 (-2.09) | -10.5 (-0.78) | loser |
| demarker | -29.3 (-2.51) | -17.1 (-1.39) | -35.0 (-3.72) | loser |
| nr7 | -57.0 (-3.44) | -33.6 (-1.49) | -55.0 (-4.06) | loser |

## Read it straight

- **dual_thrust is the batch's only clean winner**: positive on all three
  coins with positive Sharpe everywhere (BTC +3.9%, ETH +10.3%, HYPE
  +13.9%, PF up to 3.70). Caveat: only 50 combined trades — the Sharpe is
  fragile. The K-sweep (0.5/0.7/0.9) shows 0.7 sits in a stable region, not
  on a knife edge. Needs walk-forward validation before any sleeve talk.
- **HYPE flatters trend systems again** (chandelier +17%, darvas +4.4%,
  kama +8.9%): same regime artifact as batch 1 — these systems print on
  the one trending coin and bleed on BTC/ETH chop.
- **Churn is the killer on 1h**: nr7 (1,086 trades), parabolic_sar
  (1,301), awesome_oscillator (687), demarker (737) — fee drag of
  $5k–$8k combined per strategy. Daily-bar originals (Crabel NR7, Wilder
  SAR, Connors R3, Guppy GMMA) lose their edge's rarity/selectivity at 1h.
- **Port failures, honestly labeled**: connors_rsi (daily equity →
  1h crypto), nr7 (daily futures → 1h crypto), gmma (daily + compression
  filter omitted → 1h), parabolic_sar (1978 commodity dailies → 1h;
  the slower AF 0.01→0.10 variant recovers most of it — parametric, not
  structural). darvas_box's volume filter earned its keep in the sweep.
- **kama_trend's n=14 ER-window variant** (+$50 combined, HYPE Sharpe
  2.02) is the one variant across the batch worth walk-forward testing.

## Sleeve bar update (both batches)

dual_thrust joins williams_breakout and bollinger_squeeze as
positive-or-flat on all three coins — the only three of 32 that clear it.
Everything else stays research material. Nothing is for live capital.
