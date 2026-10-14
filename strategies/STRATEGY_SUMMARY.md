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

---

# Batch 3 — 2026-10-12 (14 new strategies, 84 build commits + consolidation)

14 engines built in parallel tracks and consolidated here: six classic/Wilder
systems, five more classics, and three fresh 2026 mechanisms (funding squeeze
reversal, Asia session sweep, dual-bear pullback short). Each: indicators +
signals + risk config + unit tests (369 green across the consolidated tree)
+ backtest on real Hyperliquid 1h candles (2026-03-14 → 2026-10-12,
~5,080 bars/coin). Costs: 0.045% taker + 0.01% slippage/side. Sizing: 1% risk
per trade, 3x leverage cap, $10k start. funding_squeeze_reversal also accrues
real hourly funding.

Net return % by coin (Sharpe in parens):

| Strategy | BTC | ETH | HYPE | Verdict |
|---|---|---|---|---|
| adx_dmi (Wilder, ADX≥25) | -5.2 (-0.50) | -10.0 (-1.49) | -11.8 (-1.87) | loser |
| cci_woodies (hook ±100) | -50.2 (-4.15) | -54.8 (-4.78) | +18.9 (+1.22) | mixed |
| hull_ma (HMA 16) | -69.0 (-7.39) | -50.9 (-3.98) | -38.5 (-3.02) | loser |
| aroon (Aroon 25) | -16.3 (-1.15) | +11.9 (+0.91) | +22.9 (+1.51) | mixed |
| trix (TRIX 15) | -2.7 (+0.02) | +0.6 (+0.16) | +53.3 (+2.95) | mixed |
| kst (Pring, signal 9) | -26.9 (-1.81) | -26.2 (-1.77) | +39.0 (+2.13) | mixed |
| stoch_rsi (Chande&Kroll) | -52.9 (-5.14) | -40.1 (-3.44) | -48.5 (-5.12) | loser |
| mfi (Quong&Soudack) | +3.0 (+0.33) | -38.2 (-3.46) | -22.0 (-1.92) | loser |
| obv_trend (Granville) | -56.4 (-4.00) | -38.3 (-2.15) | -7.0 (-0.27) | loser |
| pivot_breakout (floor pivots) | +5.4 (+0.43) | +8.4 (+0.56) | +5.2 (+0.43) | **WINNER** (thin) |
| lsma_slope (LSMA 21) | -30.9 (-1.52) | -54.0 (-3.41) | +31.7 (+1.59) | mixed |
| funding_squeeze_reversal | 0 trades | +$52 (1 trade) | +$385, PF 2.08 (16 trades, 68.8% WR) | mixed |
| asia_sweep | -12.1 (-1.49) | -9.6 (-1.01) | -13.1 (-1.75) | loser |
| dual_bear_short | 0 trades | -$12 (1 trade) | 0 trades | port failure (no-signal) |

## Read it straight

- **pivot_breakout is the batch's only clean winner** — positive on all three
  coins with positive Sharpe, ~108 trades/coin, stop sweep {1.5,2.0,2.5}xATR
  all positive. Honest caveat: PF ~1.06 and −20% drawdowns — a legitimate
  low-win-rate breakout system, not a reliable engine.
- **HYPE momentum is the batch's real signal.** trix (+53.3%, Sharpe 2.95,
  526 trades), kst (+39.0%, Sharpe 2.13), cci_woodies (+18.9%), and
  funding_squeeze_reversal (+$385, PF 2.08 on HYPE alone) all print on HYPE
  while BTC/ETH chop kills the same mechanics. That is 4 independent engines
  pointing the same way — a HYPE-momentum sleeve deserves its own study.
- **Classic oscillators don't survive 1h crypto.** stoch_rsi (1,339 trades),
  obv_trend (1,445), hull_ma (1,916), lsma_slope (1,158) — churn is the
  killer again: fee drag overwhelms any edge. mfi's BTC +3% is fee-level
  noise (PF 1.04); fading volume-backed momentum fails on 1h perps.
- **Session narratives don't port.** asia_sweep (stop-hunt reversal,
  PF 5.35 on XAUUSD per its author) loses uniformly on crypto (PF 0.58–0.71);
  depth sweep confirms structural failure. The forex liquidity story doesn't
  transfer to 24/7 tape.
- **Selectivity can be a no-signal trap.** dual_bear_short's four-condition
  gate fires ~0–1× per coin per 7 months — the port is unevaluable, not
  falsified. funding_squeeze_reversal's author thresholds (+0.030%/8h) are
  unreachable on HL's tame funding — BTC sat flat all 7 months; the edge, if
  any, only lives on wild-funding coins like HYPE.

## Sleeve bar update (all three batches)

pivot_breakout joins williams_breakout, bollinger_squeeze, and dual_thrust as
positive-or-flat on all three coins — the only four of 47 that clear it.
HYPE-momentum (trix, kst, cci_woodies, funding_squeeze_reversal) is the
strongest single-regime pattern in the library and the leading candidate for
a dedicated sleeve study. Everything else stays research material. Nothing is
for live capital.

---

# Batch-4 strategy summary (2026-10-13)

12 strategies, 75 build commits + 2 merge commits + infra/docs commits,
105 unit tests green. Backtests: Hyperliquid 1h candles BTC/ETH/HYPE,
2026-03-14 → 2026-10-10/13, $10k equity, 1% risk/trade, 3x leverage cap,
0.045% taker + 0.01% slippage per side, no funding accrual.
Honest verdicts — losers named.

## Batch A (classics: DeMark / Raschke / Wilder)

| slug | source | result |
|---|---|---|
| td_sequential | Tom DeMark Sequential (setup 9 + countdown 13, perfection filter, TDST) | **Earner**: ETH +$4,076 (Sharpe 2.80), BTC +$1,590; HYPE loser. Shipped: 1.5xATR stop + 96-bar hold (sweep-stable on all 3 coins) |
| holy_grail | Raschke "Holy Grail" (ADX>30-rising trend + first 20-EMA touch) | Non-earner: 11 trades in 7 months; BTC/ETH 0% WR. Gate not diluted |
| wilder_dm | Wilder DMS (DI cross + ADX>25-rising, SAR/range exits; SAR loop local) | Research-grade: 8 trades total, conjunction almost never fires on 1h |
| mass_index | Dorsey Mass Index (bulge 27/26.5; SMA(20) direction = OUR extension) | Mixed: ETH +$1,882 (Sharpe 2.06), HYPE +$157, **BTC -$927 — do not run on BTC** |

## Batch B (classics: Vortex / Camarilla / Blau / Raschke)

| slug | source | result |
|---|---|---|
| vortex | Botes & Siepman Vortex Indicator (VI+/VI- cross, ADX>20 gate shipped) | Loser on BTC/ETH at every setting; HYPE +$544 only |
| camarilla_pivots | Nick Stott Camarilla (R3/S3 fade, UTC session; breakout variant tested) | Fade loses on all 3 (59% WR, negative expectancy). Breakout/rolling variant positive but thin — not shipped |
| tsi | Blau True Strength Index (double-smoothed, signal cross, zero-gate) | **HYPE +$4,304 (Sharpe 2.73)** — batch-4 best single result; BTC/ETH losers. Coin-scoped, not general |
| raschke_anti | Raschke "Anti" (3/10/16, %D-slope trend, %K-hook re-alignment) | **Decisive loser everywhere** (BTC -$5,498, Sharpe -5.10). No param rescue |

## Batch C (Elder + fresh 2026 finds)

| slug | source | result |
|---|---|---|
| force_index | Elder Force Index (FI13 trend, FI2 pullback trigger) | Loser everywhere (2,533 trades, fee drag ~$3.4k, PF 0.53–0.89) |
| triple_screen | Elder Triple Screen (4h MACD-hist tide + FI2 wave; composes force_index) | Loser everywhere (PF 0.54–0.66); three-screen conjunction does NOT produce sparse signals (~1,030 trades) |
| rsi_extreme_edge | @Vision33X / visioneth rsi-extreme-edge (RSI(14) 1H: >90 cross-back short, <10 cross-back long; ATR 1.5x stop, 1.5R target) | **Unvalidatable on 1h**: 4 trades in 7 months. Author's coin-personality findings can't be confirmed/denied at this timeframe |
| jhadchiti_trend | jhadchiti crypto-trading-system (55-bar breakout + BTC SMA(200) regime + ±20bp/8h funding filter + coin-vs-BTC momentum) | **Mixed**: ETH +$556 (23.4% WR, 3.75x win/loss skew — author's profile; positive in 7/9 param combos); HYPE -$1,268; BTC 0 trades by construction (benchmark degenerate in momentum filter) |

## Empirical direction

Exhaustion counters (TD Sequential) and double-smoothed momentum (TSI on
HYPE) are the only positive classic systems this batch; pullback-continuation
systems (Holy Grail, Raschke Anti, Force Index) fail decisively on 1h crypto.
HYPE remains the friendliest coin for momentum systems; BTC 1h chop kills
unfiltered oscillators. Per-coin, per-strategy detail lives in each
strategy's BACKTEST.md / CALIBRATION.md.
