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

## Batch 5 (2026-10-14) — named-author classic-indicator sweep

10 strategies from documented, named-author mechanisms (Coppock, Blau,
Klinger, Chande x2, Chaikin, Elder, Mark Johnson, ChartSchool DPO, BTC
RSI+Bollinger reference). 1h bars, 2026-03-20 → 2026-10-14.

| slug | source | result |
|---|---|---|
| coppock_curve | E.S. Coppock 1962 (WMA10 of ROC14+ROC11, zero-cross) | **HYPE +$5,015 (+50.2%, Sharpe 2.61)** — batch-5 best; BTC/ETH losers. Coin-scoped, not general |
| smi_ergodic | Blau SMI Ergodic (double-EMA momentum, 5-bar signal, zero-gate) | Loser everywhere (−$7,736 combined, −$8.45/trade). Lag is structural |
| klinger_oscillator | Klinger Volume Oscillator (VF, 34/55 EMAs, 13 signal) | Loser everywhere (−$9,971, 1,742 trades). 1h volume force is chop noise |
| qstick | Chande Qstick (SMA8 of bodies, zero-cross) | **Worst in batch**: −$17,746, 2,571 trades, 26.6% WR. Noise trigger |
| rsi_bollinger | Bollinger Bands (20, 2σ) on RSI(14), midline exits | 47.4% WR and −$13,075 anyway — negative-skew machine. Killed |
| cmf_trend | Chaikin Money Flow (21) zero-cross + 200-SMA regime | Loser (−$6,658); HYPE +3.2% is noise (Sharpe 0.36) |
| chande_cmo | Chande Momentum Oscillator (±50 crosses, zero-line exits) | Loser everywhere incl. HYPE (−22.7%). Timing inverted for 1h |
| elder_ray | Elder Bull/Bear Power vs EMA(13), exhaustion entries | Loser (−$5,347); HYPE +5.4% noise. Single-bar turn detection too fast |
| dpo_cycle | Detrended Price Oscillator, causal displacement, zero-cross | Loser (−$5,835). Causal DPO is a lagged momentum osc, not a cycle timer |
| pgo | Mark Johnson Pretty Good Oscillator (±1.0 thrust entries) | Least-bad loser (−$4,785); HYPE +6.8% (Sharpe 0.54). Exit logic suspect |

## Empirical direction

Exhaustion counters (TD Sequential) and double-smoothed momentum (TSI on
HYPE) are the only positive classic systems this batch; pullback-continuation
systems (Holy Grail, Raschke Anti, Force Index) fail decisively on 1h crypto.
HYPE remains the friendliest coin for momentum systems; BTC 1h chop kills
unfiltered oscillators. Per-coin, per-strategy detail lives in each
strategy's BACKTEST.md / CALIBRATION.md.

Batch-5 addendum: slow regime systems (Coppock on HYPE, +50.2%) are the
only thing that worked; fast oscillator triggers (Qstick, Klinger, SMI,
CMO) all died on whipsaw, and the RSI+Bollinger mean-reversion showed
that a high win rate (47%) with negative skew still loses −$13k.
Causal DPO confirmed as a descriptive-not-predictive indicator.

## Batch 6 (2026-10-15) — volume-price & adaptive-average systems

10 strategies from documented, named-author mechanisms (Granville,
Arms, Dysart/Fosback, Chaikin, McGinley, Tillson, Ehlers de-lagged
ZLEMA, Glaz, Wyckoff, renko). 1h bars, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150). Costs: 0.045% taker + 0.01%
slippage/side. Sizing: 1% equity risk/trade, 3x leverage cap, $10k.

| slug | source | result |
|---|---|---|
| pvt_trend | Granville Price-Volume Trend (PVT/MA20 cross) | Loser on majors (−32%/−44%), HYPE +17.7% (Sharpe 1.02). Regime-dependent |
| ease_of_movement | Arms EMV(14) zero-cross | Loser everywhere (−49.5%/−57.6%/−13.2%, 1,760 trades). Killed |
| nvi_pvi | Dysart/Fosback NVI/EMA255 + PVI filter | Loser (−$2,715, expectancy −$10.52/trade). 255-bar "regime" ≠ 255-day regime |
| chaikin_osc | Chaikin Oscillator (3,10) zero-cross | Loser everywhere (−$16,056, 1,798 trades); (2,6) variant −$22,667. Killed |
| mcginley_dynamic | McGinley MD(10)/MD(30) cross | **Batch best**: combined +$2,640, BTC +27.4% (Sharpe 1.47), HYPE +16.7% (1.13). ETH −11.7% weak leg |
| t3_trend | Tillson T3(5)/T3(15) cross, a=0.7 | Mixed: HYPE +30.3% (Sharpe 1.54), majors losers, combined −$1,301 |
| zlema_cross | De-lagged ZLEMA(10)/ZLEMA(30) cross | Loser on majors (−62.8%/−45.7%); "zero lag" = faster whipsaw. Slow (20,60) variant flips positive |
| qqe | Glaz QQE Fast-TL/Slow-TL cross (4.236) | **HYPE star**: +61.8% (Sharpe 2.48, PF 1.29); majors −40%/−37%. Coin-scoped |
| wyckoff_spring | Wyckoff spring/upthrust, 50-bar range | Mixed: ETH +25.8% (1.14) on 20% win rate = lottery; BTC/HYPE losers |
| renko_trend | 0.5xATR renko brick reversals | **Worst in batch**: −$19,662, 2,571 trades, Sharpe −7.44 BTC. Killed |

## Empirical direction

Slower beats faster in every calibration sweep this batch (PVT MA40,
EMV28, NVI EMA500, CHO 6/21, MD 20/60, T3 8/21, ZLEMA 20/60, brick
1.0xATR all beat their fast counterparts) — 1h churn is the structural
killer, and de-lagging/fast smoothing just manufactures whipsaw. The two
systems worth remembering are both slow adaptive MAs: McGinley (the only
positive-combined system in the batch) and QQE-on-HYPE (+61.8%, the
batch's best single print, same HYPE-momentum story as Coppock). Renko
confirmed as a fee-donation machine on 1h perps. Per-coin, per-strategy
detail lives in each strategy's BACKTEST.md / CALIBRATION.md.

Batch-6 addendum: the "volume" half of the theme mostly failed —
EMV, Chaikin, NVI/PVI, PVT all lose on majors — because 1h volume flow
is bar-noise, not the multi-day accumulation these authors designed
for. The adaptive-average half (McGinley, T3, ZLEMA-slow, QQE) is where
the batch's only wins live.

## Batch 7 (2026-10-16) — published systems + classic patterns

12 strategies from documented, named-author mechanisms (Shannon, Ehlers,
L. Williams x2, Wilder-lineage divergence, classic price action, Raschke,
Bonde, Minervini, Dorsey/Wheeler, Gann). 1h bars, 2026-03-14 → 2026-10-15
(BTC/ETH 5,157 bars; HYPE 5,155). Costs: 0.045% taker + 0.01% slippage/side.
Sizing: 1% equity risk/trade, 3x leverage cap, $10k. 111 unit tests green.

| slug | source | result |
|---|---|---|
| anchored_vwap | Shannon AVWAP reclaim (fractal anchors) | HYPE +19.6% (Sharpe 1.69); BTC −22.9%, ETH −14.2%. Coin-scoped |
| rvi_ehlers | Ehlers RVI / weighted signal-line cross | BTC +16.1% (0.89); ETH −4.1%, HYPE −19.5%. Unfiltered = whipsaw |
| ultimate_osc | Williams UO(7,14,28) divergence (1985 rules) | Loser everywhere (−19.1%/−9.2%/−7.6%). Divergence marks pauses, not reversals |
| rsi_divergence | RSI(14) regular divergence + confirmation | −3.8%/−4.3%/−5.9%, 22 trades. Too sparse; pivot lag eats entries |
| inside_bar | Inside-bar mother-bar breakout, EMA50 bias | HYPE +10.1% (0.83); BTC −15.1%, ETH −0.9%. Chop victim on majors |
| raschke_tail | Raschke "Tail" at 20-bar extremes | Loser everywhere (−18.1%/−5.9%/−5.9%) |
| episodic_thrust | Bonde Episodic Pivot (crypto volume/range proxy) | 8 trades in 7 months (−2.3%/+0.6%/+2.1%). Inconclusive — no edge shown |
| williams_pct_r | Williams %R 5-bar extreme trigger (1979) | **Worst in batch**: −40.9%/−43.1%/−48.3%, 890 trades. Trigger wrong for 1h |
| minervini_trend | Minervini Trend Template (long-only) | 7 trades, UNTESTABLE — 4,900-bar warmup leaves ~258 tradeable bars |
| point_figure | P&F 3-box reversal, 0.5xATR boxes | **Batch winner**: +10.8%/+8.7%/+13.1% all green. Thin PFs (1.05–1.12); walk-forward wanted |
| gann_swing | Gann 1-bar/3-bar swing system | **Rejected**: −74.3%/−59.8%/−23.3%, 1,733 trades. 1-bar churn blowup |
| key_reversal | Key reversal bar, 20-bar extreme | Mixed+: ETH +12.6% (1.79), HYPE +9.3% (1.32), BTC −3.1% |

## Empirical direction

Point & Figure is the batch's only all-coin winner — and it wins the way
this library keeps winning: by being SLOW. Box-filtered trend capture beat
every oscillator in the batch. But profit factors are 1.05–1.12 — a working
edge, not a proven one; it needs walk-forward before any promotion talk.
The HYPE-scoped story repeats: anchored_vwap (+19.6%) and inside_bar
(+10.1%) print only on HYPE and bleed on BTC/ETH — same 2026-HYPE-parabola
regime as batch 6's QQE, not general alpha. Divergence is dead on 1h:
ultimate_osc, rsi_divergence, williams_pct_r all lose — on hourly crypto,
momentum divergence marks a pause, not a reversal, and Williams' published
%R trigger (−100, wait 5 bars, hook back) is the single worst system in the
batch. Two honest non-results: minervini_trend cannot be evaluated (the
200-day template needs a 4,900-bar warmup on 1h; 7 trades), and
episodic_thrust's 8 trades say nothing — Bonde's catalyst mechanism does not
port to hourly bars without real catalysts. Both are port failures, not
strategy failures. Gann's 1-bar swing is the blowup (−74% BTC): single-bar
direction changes are pure chop on 1h; the 3-bar trend half was fine, the
1-bar timing half killed it.

## Batch 8 (2026-10-17) — 12 systems: named-author classics + SMC mechanics

12 strategies, each: indicators + signals + risk config + unit tests (63 green)
+ backtest on real Hyperliquid 1h candles (2026-03-14 → 2026-10-17, ~5,000
bars/coin). Costs: 0.045% taker + 0.01% slippage/side. Sizing: 1% equity
risk/trade, 3x leverage cap, $10k. Rough batch: 7 losers, 4 mixed, 1 flat.

Net return % by coin (Sharpe in parens):

| Strategy | BTC | ETH | HYPE | Verdict |
|---|---|---|---|---|
| momentum_pinball (Raschke LBR/RSI) | -67.7 (-5.16) | -69.5 (-5.62) | -55.0 (-3.89) | loser (port failure: 706 trades, costs eat 2x equity) |
| tdi (Dean Malone TDI) | -83.6 (-12.95) | -82.1 (-12.19) | -75.1 (-11.54) | loser (1,282 trades of green/red whipsaw) |
| half_trend (everget HalfTrend) | -10.9 (-1.57) | -7.5 (-1.20) | +1.0 (+0.21) | flat (33-40 trades; slow filter, no edge) |
| vidya (Chande VIDYA) | -12.5 (-1.35) | -6.3 (-0.68) | -2.9 (-0.35) | loser (adaptivity ≠ edge) |
| frama (Ehlers FRAMA) | -17.8 (-2.12) | -7.3 (-0.63) | -7.1 (-0.99) | loser (alpha correct, signal loses) |
| liquidity_sweep (ICT stop-hunt fade) | -24.3 (-2.80) | -14.9 (-1.69) | -17.2 (-2.04) | loser (54-56% WR, negative skew: short the breakout tail) |
| market_structure (BOS/CHoCH) | -30.8 (-1.93) | -31.3 (-1.93) | **+32.0 (+1.74)** | mixed (HYPE edge stable at (3,3) pivots: +32.9) |
| candle_patterns (engulfing + pin) | -87.6 (-9.21) | -87.1 (-9.69) | -53.1 (-3.54) | loser (port failure: 1h patterns are noise) |
| linreg_channel (Raff channel fade) | -52.5 (-4.29) | -47.0 (-3.90) | -41.2 (-3.43) | loser (tags fade into riding trends) |
| choppiness (Dreiss CHOP + Donchian) | +6.2 (+0.70) | -27.1 (-3.35) | +6.9 (+0.81) | mixed (thin; regime gate works, ETH bleeds) |
| vwma_cross (VWMA 20/50 + volume) | -5.9 (-0.65) | -2.5 (-0.20) | +20.0 (+1.87) | mixed/unstable ((10,30) moves the edge to ETH: fluke) |
| ribbon_trend (EMA 8/13/21/34/55) | -14.3 (-1.41) | -18.0 (-2.09) | **+17.3 (+1.36)** | mixed (HYPE edge survives MIN_FAN=0.008: +26.2) |

## Empirical direction

The batch's lesson is costs and timeframe, not indicators. Momentum Pinball
and candle_patterns are port failures of the same kind: systems designed for
daily bars / first-hour entries that fire hundreds of times on 1h crypto —
at 0.11% round-trip on ~3x notional, 700+ trades cost more than the account.
TDI is the extreme: 1,282 green/red crosses, 24-29% win rate. The adaptive
averages (VIDYA, FRAMA) verify perfectly as indicators and still lose —
adaptivity solves lag, not direction. Liquidity-sweep is the interesting
loser: 54-56% win rate, negative expectancy — fading hunts wins the small
battles and pays the breakout tail. The HYPE regime story repeats for the
fourth batch: market_structure (+32.0%, stable across pivot sizes) and
ribbon_trend (+17.3%, better at stricter fan) print on HYPE and bleed on
choppy BTC/ETH. vwma_cross is the cautionary tale: the (10,30) sweep moves
the "edge" to ETH — when the winner changes coins with the parameter, it was
never an edge. choppiness is the only system that wins by sitting out:
+6.2/+6.9 on 70-odd trades, and the honest counterweight is ETH −27.1%.

## Batch 9 (2026-10-18) — named-author classics sweep (Elder, DeMark, Wilder, Williams, Carver, Sperandeo, Hurst, Taylor, Unger, Ehlers, Raschke, ICT)

12 strategies from documented, named-author mechanisms. 1h bars,
2026-03-14 → 2026-10-18 (BTC/ETH/HYPE ~5,224 bars each). Costs: 0.045%
taker + 0.01% slippage/side. Sizing: 1% equity risk/trade, 3x leverage
cap, $10k.

| slug | source | result |
|---|---|---|
| td_combo | Tom DeMark TD Combo (9-setup + 13-countdown) | Thin scratch: +$432 combined on 15 trades. Ungradable sample — setups barely fire on 1h |
| ehlers_cyber_cycle | John Ehlers Cyber Cycle (alpha=0.07, trigger cross) | **Worst churn in library**: −$28,060 combined, 6,833 trades. Killed |
| raschke_3_10 | Linda Raschke 3/10 oscillator (signal-line cross) | Loser everywhere (−$8,872, 953 trades) |
| elder_impulse | Alexander Elder Impulse System (EMA13 + MACD hist) | Loser (−$27,044, 3,532 trades); exit-on-flip churns ~1 trade/4.4 bars. Killed |
| wilder_swing_index | Welles Wilder Swing Index / ASI (20-bar breakout) | Loser (−$7,333 combined) |
| williams_alligator | Bill Williams Alligator + fractal breakout | Loser (−$6,273 combined) |
| carver_ewmac | Rob Carver EWMAC forecast (+/−10 bands) | **Batch best**: combined +$807, BTC +8.2% (0.68), ETH +8.7% (0.68), HYPE −8.9%. Mixed/regime-dependent |
| sperandeo_123 | Victor Sperandeo 1-2-3 trend change | Loser (−$773 combined; BTC −9.5% decisive) |
| ict_silver_bullet | ICT Silver Bullet (FVG + MSS in NY killzones) | Loser (−$379) on 13 trades in 7 months — conjunction never fires. Ungradable |
| hurst_fld | J.M. Hurst FLD(20/40/80) cascade | Loser (−$6,032 combined); cascade filter only brakes churn |
| taylor_3day_cycle | George Douglass Taylor 3-day Book Method | Loser (−$5,973 combined; BTC −40.7%) |
| unger_opening_breakout | Andrea Unger 3h opening-range breakout | Loser (−$11,759); no session structure in 24/7 crypto. Port failure |

## Empirical direction

The big-name systems port worst. Elder, Ehlers, and Unger are churn
machines on 1h crypto — ehlers_cyber_cycle's 6,833 trades at 0.11%
round-trip is a fee-donation system with an indicator attached, and
elder_impulse's exit-on-any-flip is the same failure in a different
font. The discretionary classics (Sperandeo 1-2-3, ICT Silver Bullet,
Taylor cycle) barely fire at this granularity: ict_silver_bullet took
13 trades in 7 months because four independent conditions never align
on hourly bars — faithful ports of tape-reading systems need
lower-timeframe data. Carver's EWMAC is the batch's only live pulse:
+8.2%/+8.7% on BTC/ETH (Sharpe 0.68 each) with the same HYPE failure as
every other trend system — and the calibration sweep is the lesson
(keep the shipped 3-rule blend; the better single-rule variant is
in-sample selection). The HYPE regime story repeats for a fifth batch:
trend systems print on the parabolic alt and bleed on choppy majors.
td_combo is the honest curiosity: +$432 on 15 trades says nothing, but
the mechanism fired almost never — DeMark's setup is a daily-chart
system, and on 1h it is a museum piece. Per-coin, per-strategy detail
lives in each strategy's BACKTEST.md / CALIBRATION.md.

## Batch 10 (2026-10-19) — indicator/author classics not yet in the library (Williams, Chande, Twiggs, Mulloy, Ehlers, Murrey, Kagi, 3-line-break, fractals, harmonics, Fib)

12 strategies from documented, named mechanisms, all new vs the 114-dir
main tree (duplicate candidates kst/tsi/vortex/rvi/trix/ultimate_osc/
force_index/vidya/stoch_rsi/rsi_divergence/klinger/mass_index/camarilla/
half_trend/linreg_channel were rejected against the remote tree). 1h bars,
2026-03-14 → 2026-10-19 13:00 UTC (BTC/ETH 5,247 bars, HYPE 5,245). Costs:
0.045% taker + 0.01% slippage/side. Sizing: 1% equity risk/trade, 3x
leverage cap, $10k. 139 new unit tests green.

| slug | source | result |
|---|---|---|
| williams_ad | Larry Williams A/D (WAD/SMA20 cross, price SMA50 gate) | Loser: −$10,361 combined, 1,133 trades, PF 0.60–0.75. Confirmation arrives after the move |
| cvd_divergence | CVD (close-location approx) regular divergence | Loser: −$5,076 combined, 763 trades. Re-enters longs on every bar of a decline |
| chande_forecast_osc | Chande Forecast Oscillator (FO/3-bar signal cross) | **Worst churn in library**: −$18,561 combined, 2,832 trades (~1/5 bars), $15,659 fees |
| twiggs_money_flow | Twiggs Money Flow (21-period, zero-line cross) | Loser: −$8,478 combined, 1,401 trades; HYPE +$192 only green print |
| tema_trend | Mulloy TEMA20/50 cross, SMA200 filter | Flat: +$131 combined on 341 trades. HYPE +$2,131 (Sharpe 2.14, PF 1.63), BTC −$1,750 |
| harmonic_gartley | Gartley XABCD (±6% ratio stack) | Inconclusive: 2 trades in 7 months, −$216. Detector verified on synthetic patterns |
| laguerre_rsi | Ehlers Laguerre RSI (γ=0.5, 0.2/0.8 reversals) | Loser: −$13,464 combined, 2,069 trades. Per-bar (not cumulative) LRSI per source |
| fibonacci_pullback | Fib 50–61.8% pocket reclaim, swing-high target | **Batch best**: +$2,723 combined, 274 trades. ETH +$1,375 (0.79), HYPE +$1,830 (1.13), BTC −$482 |
| fractal_breakout | Bill Williams 5-bar fractals, SMA200 filter | Loser: −$7,952 combined, 945 trades |
| murray_math | Murrey Math 64-bar octave, extreme-zone reversals | Loser: −$4,329 combined, 532 trades, all three coins |
| kagi_trend | Kagi 4×ATR reversal, yin/yang transitions | Mixed: +$2,057 combined, 69 trades. BTC +$3,371 (Sharpe 2.70, PF 2.73), ETH/HYPE negative |
| three_line_break | 3-line-break turnaround entries | No evaluable edge: 10 trades, +$9 combined. Under-trades at 1h |

## Empirical direction

The honest-loser pattern holds for a sixth batch: 8 of 12 lose outright,
and the two "winners" are coin-regime artifacts — fibonacci_pullback wins
only on ETH/HYPE while BTC bleeds, kagi_trend's +$2,057 is one BTC run
(+33.5%, Sharpe 2.70) against two losing coins. chande_forecast_osc
(-$18,561, 2,832 trades) replaces ehlers_cyber_cycle as the library's
worst churn machine: a 3-bar signal line on a regression oscillator
crosses roughly once every five bars on 1h crypto. The two
never-fire systems (harmonic_gartley: 2 trades; three_line_break: 10)
are the daily-chart problem in miniature — classical ratio/pattern
completeness rarely survives hourly granularity. CVD divergence and
fractal breakouts both lose the same way: re-entering into continuation
moves. The HYPE regime story repeats: tema_trend prints +21.3% on HYPE
and −17.5% on BTC. Per-coin, per-strategy detail lives in each
strategy's BACKTEST.md / CALIBRATION.md.

## Batch 11 (2026-10-20) — volatility/filter classics + statistical systems + classic patterns (Williams, Waddah Attar, Legoux, Ehlers, Kalman, VPIN, OU, volume profile, Chesler, Ross, O'Neil)

12 strategies from documented, named mechanisms, all new vs the 126-dir
main tree (checked against the remote tree before building). 1h bars,
2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC (BTC/ETH ~5,271 bars, HYPE
~5,269; cache extended a few bars during the build). Costs: 0.045%
taker + 0.01% slippage/side, funding not modeled. Sizing: 1% equity
risk/trade, 3x leverage cap, $10k. 159 new unit tests green.

| slug | source | result |
|---|---|---|
| vix_fix | Larry Williams VIX Fix (WVF(22), BB(20,2.0), 24-bar max hold) | Loser: −$6,178 combined, 802 trades, PF 0.81. Midline exit books bounces, the 2xATR stop takes the breakdowns |
| waddah_attar | Waddah Attar Explosion (sens 150, hist above explosion line + dead zone) | Loser: −$5,813 combined, 719 trades, PF 0.67. Entries chase momentum acceleration, buy burst tops |
| ssl_channel | SSL SMA(10) high/low channel flips | Loser: −$10,083 combined, 1,284 trades, PF 0.80. Fees $7,856. n=20 on HYPE +$2,636 flagged in calibration but not adopted |
| alma | ALMA 9/21 cross + 20-bar high/low confirmation | **Batch best**: +$2,186 combined, 233 trades. Positive on all 3 coins; ETH near-noise (PF 1.06, $3/trade) |
| mama_fama | Ehlers MAMA/FAMA Hilbert-adaptive cross | Loser: −$11,909 combined, 1,660 trades, PF 0.69. MAMA hugs price, crosses ~1/9 bars |
| kalman_trend | Kalman price+velocity filter, cross + slope | **Second-worst in the library**: −$19,946 combined, 3,102 trades, PF 0.59–0.66. Near-zero-lag filter = price with extra steps |
| vpin | VPIN toxicity exhaustion (90th pct + 20-bar extreme) | Loser: −$3,545 combined, 178 trades, PF 0.65. Experimental read: toxicity predicts volatility, not direction |
| ou_zscore | OU half-life z-score mean reversion | Loser: −$8,112 combined, 451 trades, PF 0.67. BTC Sharpe −3.3 |
| volume_profile | Value-area fade (VAL/VAH reclaim, 70% VA) | Loser: −$2,969 combined, 254 trades, PF 0.81. Roughly cost-dragged to zero before fees |
| hikkake | Chesler Hikkake false-breakout (2004) | Loser: −$4,367 combined, 364 trades, PF 0.72–0.94. 35–38% WR can't clear the 2R breakeven |
| ross_hook | Joe Ross 1-2-3 + hook continuation | Loser: −$3,921 combined, 327 trades, PF 0.63–0.90. Mechanical pivots fire on too many low-quality setups |
| cup_handle | O'Neil cup & handle breakout | No evaluable edge: 0 trades. 1h crypto cup depth (median ~20xATR) is mutually exclusive with the spec's 1–4xATR band |

## Empirical direction

The honest-loser streak holds for a seventh batch: 10 of 12 lose, one
never fires, and the one winner (alma, +$2,186) is the thinnest book of
the day at 233 trades with ETH contributing a near-noise PF 1.06. The
batch's real story is the zero-lag trap: kalman_trend (−$19,946, 3,102
trades) and mama_fama (−$11,909, 1,660) both track price so tightly that
the filter cross is just a lagged price cross — chop turns them into
fee-donation systems with indicator branding, and both are robust losers
by trade count, not noise. The pattern ports repeat the batch-9 lesson:
hikkake and ross_hook lose on hourly granularity where discretionary
filters (Chesler's 3-bar confirmation discipline, Ross's own "wait for
the hook") can't be coded without overfitting, and cup_handle is the
daily-chart problem in its purest form — the detector is verified on
synthetic patterns but the real 1h data admits zero candidates. The two
statistical systems earned their keep in the limitations sections:
ou_zscore's build exposed that deviations from a trailing SMA are
mechanically mean-reverting, so the half-life gate admits random walks
instead of filtering them; vpin's fade is systematically early because
the academic metric flags toxicity ahead of volatility, not direction.
ssl_channel's calibration bright spot (n=20, HYPE +$2,636, PF 1.18) is
flagged for out-of-sample follow-up, not adopted. Per-coin, per-strategy
detail lives in each strategy's BACKTEST.md / CALIBRATION.md.

## Batch 12 (2026-10-21)

12 new strategies shipped, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21,
~5,295 bars/coin). Costs: 0.045% taker + 0.01% slippage/side. Sizing: 1%
equity risk/trade on the ATR stop, 3x leverage cap, $10k. 142 new unit
tests green.

| slug | source | result |
|---|---|---|
| vortex | Vortex Indicator (Botes & Siepman), VI(14) cross | Loser: −$8,576 combined, 1,676 trades, PF 0.66–0.96. Raw VI cross whipsaws on 1h (~2.5 trades/day); BTC Sharpe −3.85, MaxDD −55.5% |
| trix | TRIX (Hutson), 14/9, turn-from-extreme filter | +$5,290 combined, 545 trades — **HYPE-carried**: HYPE +$5,573 (Sharpe +2.94, PF 1.50); BTC −$724, ETH +$441 (fees 4x net) |
| coppock_curve | Coppock Curve (1962), WMA(10) of ROC14+ROC11 | Loser: −$535 combined, 779 trades. Monthly indicator shoehorned onto 1h; HYPE +$3,089 is the only green leg |
| kst | Know Sure Thing (Pring), 10/15/20/30 + signal 9 | +$1,449 combined, 606 trades — **HYPE-only**: HYPE +$5,582 (Sharpe +2.89); BTC −$2,287, ETH −$1,846 |
| obv_divergence | Granville OBV + pivot-confirmed divergence | Loser: −$551 combined, 49 trades. k=10 confirmed divergences too rare on 1h to be tradeable |
| elder_force_index | Force Index (Elder), FI2 timer + FI13 trend gauge | Loser: −$8,224 combined, 1,051 trades, PF 0.67–0.89. FI2 zero-cross pullback churns into chop; BTC MaxDD −44.7% |
| klinger_osc | Klinger Volume Oscillator (34/55/13) | **Batch worst**: −$13,767 combined, 2,122 trades, PF 0.63–0.86. Cumulative-range `cm` saturates; every swept setting loses on every coin |
| pretty_good_osc | Pretty Good Oscillator (Mark Johnson), ±3 breakout | Inconclusive: +$282 combined, 201 trades. BTC/ETH dead; the only green is a thin 48-trade HYPE leg (+$1,535) |
| stoch_rsi | Stochastic RSI (14,14,3,3) | Loser: −$4,505 combined, 891 trades. BTC −$4,524 (Sharpe −3.44); the 20/80 exhaustion trigger whipsaws on 1h |
| woodies_cci | Woodies CCI zero-line reject (14/6) | Loser: −$1,385 combined, 233 trades, WR 23.6%. Gross of fees +$481; $1,867 of fees makes it a steady loser |
| elder_triple_screen | Elder Triple Screen (6h MACD + FI2 pullback) | Loser: −$6,702 combined, 548 trades. 6h trend screen arrives too late on 1h; verified 89.7% WR on synthetic uptrend, so the signal is anti-predictive here, not buggy |
| lbr_holy_grail | Holy Grail (Raschke), ADX>30 + 20EMA pullback | No evidence: −$137 combined, 15 trades in 7 months. ADX(14)>30+rising is rare on 1h; the daily setup doesn't transfer |

## Empirical direction

The honest-loser streak holds for an eighth batch: 8 of 12 print red
combined, the 2 green ones (trix, kst) are HYPE-only regime luck with
BTC/ETH firmly red, pretty_good_osc is a noise-level +$282, and
lbr_holy_grail barely trades. The batch's through-line is trigger
churn: volume-acceleration pullbacks (elder_force_index, klinger_osc,
stoch_rsi) fire 2,000–1,000 trades and donate to fees; the raw VI
cross (vortex) repeats the batch-11 zero-lag lesson at 1,676 trades.
Indicators designed for slower clocks fail at 1h the same way:
coppock's monthly construction, the triple screen's 6h MACD tide,
woodies' 6-bar persistence, and Raschke's daily ADX gate all arrive
late or never fire. The pullback-to-structure family (holy grail,
obv_divergence) suffers the opposite disease — patterns too rare to
trade. Nothing here is anywhere near a live gate. Per-coin detail
lives in each strategy's BACKTEST.md / CALIBRATION.md.

## Batch 13 (2026-10-22)

12 new strategies shipped, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h (BTC/ETH/HYPE, 2026-03-14 -> 2026-10-21,
~5,300 bars/coin). Costs: 0.045% taker + 0.01% slippage/side. Sizing: 1%
equity risk/trade on the ATR stop, 3x leverage cap, $10k. 212 new unit
tests green.

| slug | source | result |
|---|---|---|
| detrended_price_oscillator | DPO(20) zero-line cross + SMA50 trend filter | Loser: -$4,738 combined, 757 trades, WR 24.2%. The 11-bar displacement makes entries structurally late: buys cycle tops, sells cycle bottoms |
| ulcer_index | Ulcer Index(14) long-only regime gate + Donchian-20 breakout | Inconclusive: +$1,598 combined, 335 trades - but fee-bound noise (ETH/HYPE nets ~= their fees) and Martin's 5/10 UI thresholds are out of scale for 1h bars (UI lives in 0-4); effectively a Donchian long-only wearing an Ulcer Index costume |
| chaikin_volatility | Chaikin Volatility(10/10) threshold cross + SMA50 filter | Loser: -$9,944 combined, 973 trades. Trades *into* volatility expansion - the wrong side of Chaikin's own observation: spikes mark climactic participation |
| dema_trend | DEMA(21/55) cross (Mulloy) | Loser: -$632 combined, 514 trades, PF 0.85-1.06. Mulloy's lag reduction reacts to moves that don't persist; all swept settings lose |
| ehlers_supersmoother | SuperSmoother(20) slope-gated price cross | Loser: -$7,047 combined, 914 trades, WR 26.3%. Slope gate halves the loss vs raw crosses, but entries still arrive when legs are spent |
| ehlers_decycler | Decycler(20) price cross | Loser: -$15,448 combined, 1,900 trades, WR 26.2%. Zero-lag is the flaw: price crosses the lag-free trend line constantly; every swept cutoff loses |
| ehlers_reflex | Reflex(20) zero-cross | Inconclusive: -$982 combined, 607 trades, PF 0.96. BTC -$2,290, ETH/HYPE near-noise; the naked zero-cross needs a chop filter |
| oops_pattern | Larry Williams Oops, 24-bar session | +$3,176 combined, 526 trades - **HYPE-only**: HYPE +$6,652 (Sharpe +2.80, PF 1.48); BTC -$3,501, ETH +$25. Fading breakdowns only works where they snap back |
| turtle_classic | Original Turtle S1(20/10)+S2(55/20) with skip rule | Breakeven noise: +$332 combined, 254 trades, PF 1.02. The skip rule self-extinguishes on 1h (>90% of entries are S2 failsafe); BTC an outright loser |
| accelerator_oscillator | Bill Williams AC(5/34/5), 2/3-bar color rule | **Batch worst**: -$25,444 combined, 3,113 trades, PF 0.38-0.65. A whipsaw machine: ~1,000 trades/coin at 30-37% win rate |
| gator_oscillator | Bill Williams Gator states + fan direction | Loser: -$7,538 combined, 1,025 trades. The 8-bar-displaced balance lines fan after the leg ends; eats expansion marks exhaustion, not initiation |
| balance_of_power | Livshin BOP(14) zero-cross | Loser: -$15,141 combined, 2,264 trades, WR 26.0%. The smoothed BOP cross is too slow a trigger for 1h crypto; 800+ whipsaw trades/coin feed the fee man |

## Batch 14 (2026-10-23)

12 strategies built, 9 shipped (elder_ray, smi_ergodic, rsi_divergence were
built and tested but SKIPPED as duplicates - first-shipped versions from
earlier batches kept per the duplicate rule; the branch's overwrites were
reverted). Each shipped strategy: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h (BTC/ETH/HYPE, 2026-03-14 -> 2026-10-22,
~5,330 bars/coin). Costs: 0.045% taker + 0.01% slippage/side. Sizing: 1%
equity risk/trade on the ATR stop, 3x leverage cap, $10k. 176 new unit
tests green. All 9 shipped print red: combined -$69,139 across 5,621 trades.

| slug | source | result |
|---|---|---|
| ultimate_oscillator | Larry Williams UO(7/14/28), 3-step divergence method | Loser: -$798 combined, 41 trades, WR 26.8%. Divergence setups are rare (~1 per coin per fortnight) and the breakout trigger fires after the snapback is priced in; ETH 0-for-7 |
| true_strength_index | William Blau TSI(25/13) + signal(7), zero-territory filter | Loser: -$7,855 combined, 507 trades, Sharpes -1.6 to -3.4. Double smoothing is elegant on daily bars and late on 1h: crosses confirm after the move is spent |
| wave_trend | LazyBear WaveTrend(10/21), cross-in-zone +/-53 | Loser: -$5,656 combined, 430 trades. Loses gross of fees (~-$1,720 ex-fees): the +/-53 lines fire late into exhausted moves on 1h crypto |
| fair_value_gap | ICT/SMC 3-candle imbalance retest, 1.5xATR displacement | Loser: -$5,440 combined, 486 trades. The displacement filter is far too weak on 1h: zones active 53-61% of bars, so "imbalances" are ordinary volatility; 64-75% die on the 2xATR stop |
| pin_bar_reversal | Pring pin bar (2/3 tail) at 5-bar swing extremes | Loser: -$10,378 combined, 579 trades, PF 0.72. Violent 1h wicks read as stop-hunts/continuation, not absorption; 35% win rate can't clear a 2R break-even |
| inside_bar_breakout | Strict inside bar, mother high/low breakout, 5-bar expiry | Loser: -$14,075 combined, 1,471 trades. 17.4% of bars are inside bars: ~1 trade per 10 bars at 36-39% win rates; breakouts of 1h mother levels are noise, not expansion |
| engulfing_pattern | Body-engulf + EMA(20) trend alignment, act on close | Loser: -$13,431 combined, 1,325 trades, PF 0.54-0.91. Negative gross before costs (BTC Sharpe -5.57): the EMA trend filter admits everything the raw pattern fires, and the canon's location half (structure/S&R) is missing |
| breakout_retest | 20-bar range breakout, clean throwback retest, 20-bar window | Loser: -$8,578 combined, 556 trades, PF 0.68-0.87. The 1.0xATR stop takes ~64% of trades; the level-loss signal exit fires only ~7% - retests that hold are the minority |
| vwap_cross | Rolling 24-bar VWAP cross + slope + 1.2x volume | Loser: -$2,928 combined, 226 trades. Slope/volume filters are nearly always satisfied on 1h bars, so it behaves like a bare VWAP cross - a whipsaw machine; shorts bleed hardest |

## Empirical direction

The honest-loser streak holds for a tenth batch: all 9 shipped strategies
print red combined, -$69,139 across 5,621 trades, with inside_bar_breakout
(-$14,075) the worst of the shipped set. Three more (elder_ray, smi_ergodic,
rsi_divergence) were built and tested in this batch but skipped as
duplicates of first-shipped versions - and notably, all three duplicates
were ALSO losers in their original form, which is its own kind of
replication. The through-line now spans indicator families and the
price-action canon alike: classic oscillators (TSI, WaveTrend, UO) lose
because their daily-bar tuning is late on 1h crypto, and the discretionary
price-action patterns (pin bars, engulfings, inside bars, FVGs, throwbacks)
lose because their edge lives in location and selectivity - swing structure,
support/resistance, confirmed exhaustion - which the mechanized 1h versions
replace with frequency. Nothing here is anywhere near a live gate.
Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.

## Batch 15 (2026-10-24)

12 new strategies shipped, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h (BTC/ETH/HYPE, 2026-03-14 22:00 UTC ->
2026-10-22 23:00 UTC, BTC/ETH 5,335 bars, HYPE 5,333). Costs: 0.045%
taker + 0.01% slippage/side. Sizing: 1% equity risk/trade on the ATR stop,
3x leverage cap, $10k. 197 new unit tests green. All 12 shipped print
red-or-flat combined: -$111,696 across 12,842 trades.

| slug | source | result |
|---|---|---|
| elder_safezone | Elder SafeZone (Come Into My Trading Room) + EMA22 cross | Loser: -$8,644 combined, 1,202 trades, PF 0.61-0.89. SafeZone barely filters the bare EMA cross |
| slow_stochastic | Lane Slow Stochastic %K(14)/%D(3) in 20/80 zones | Loser: -$12,184 combined, 940 trades, PF 0.44-0.68. Zone crosses whipsaw |
| cci_extreme | Lambert CCI(20) cross back through +/-100 | Loser: -$5,766 combined, 872 trades. ETH nearly flat (-$422, PF 0.96) |
| bollinger_pctb | Bollinger %B reclaim of 0 / loss of 1, exit at 0.5 | Loser: -$8,995 combined, 741 trades. 605 of 741 trades exit on the stop |
| keltner_squeeze | TTM-style squeeze (BB width < KC width) + band breakout | Mixed: +$900 combined, 408 trades. ETH +$2,042 only green leg; signal exit nearly decorative (12 of 408) |
| golden_cross | SMA(50)/SMA(200) cross | Thin loser: -$1,466 combined, 95 trades. 93 of 95 exit on the stop — lagging cross confirms after the move |
| chaikin_adl_trend | Chaikin ADL vs SMA(10) + SMA50 price gate | Loser: -$16,483 combined, 1,512 trades, PF 0.52-0.78. Loses before fees too |
| rsi_ma_cross | RSI(14) vs SMA(14) of RSI | **Batch worst**: -$22,746 combined, 2,744 trades, PF 0.55-0.74. Near-perfect long/short symmetry is structural |
| ehlers_instantaneous | Ehlers Instantaneous Trendline (alpha 0.07) price cross | Loser: -$22,082 combined, 2,448 trades, PF 0.55-0.69. Second-worst in batch |
| ehlers_roofing | Ehlers Roofing Filter (48-bar HP + SuperSmoother 10) zero cross | Loser: -$13,043 combined, 1,559 trades, PF 0.62-0.90. ~71% stop exits |
| order_block_retest | ICT/SMC order-block retest after >=1.5xATR displacement | Mild loser: -$1,146 combined, 288 trades. ETH -$35 is flat; no edge shown |
| abcd_pattern | ABCD harmonic (BC 38.2-88.6%, CD 127.2-161.8%, \|CD\|~= \|AB\|) | Inconclusive: -$41 combined on 33 trades. HYPE +$717 on 11 trades is noise |

## Empirical direction

The honest-loser streak holds for an eleventh batch: 10 of 12 lose
outright, keltner_squeeze is a +$900 mixed print carried by one ETH leg,
and abcd_pattern's 33 trades say nothing. The batch's through-line is
the cross trap in both directions: fast crosses (RSI-vs-its-average,
Instantaneous Trendline, Roofing zero-line, ADL-vs-average) fire
2,000+ times and donate to fees, while slow crosses (golden cross,
ABCD) confirm after the move or almost never fire. SafeZone is the
batch's cautionary filter: a respected exit discipline barely changes
the bare EMA cross it is supposed to protect (-$8,644 vs the same
churn). The SMC half repeats batch 14: order blocks retest into
continuation as often as reversal, and harmonic completeness at 1h
granularity is a museum piece (33 completions in 7 months). Nothing
here is anywhere near a live gate. Per-coin detail lives in each
strategy's BACKTEST.md / CALIBRATION.md.

## Batch 16 (2026-10-25)

12 new strategies shipped, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h (BTC/ETH/HYPE, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC, BTC/ETH 5,379 bars, HYPE 5,377). Costs: 0.045%
taker + 0.01% slippage/side. Sizing: 1% equity risk/trade on the ATR stop,
3x leverage cap, $10k. 87 new unit tests green. Combined -$60,971 across
10,590 trades — a number dominated by two structural failures (see below).

| slug | source | result |
|---|---|---|
| ema_cross | EMA(9)/EMA(21) crossover (Murphy) | Loser: -$2,054 combined, 729 trades, PF 0.78-1.11. HYPE +$1,147 only green leg |
| sma_cross | SMA(20)/SMA(50) crossover (Murphy) | Loser: -$2,412 combined, 375 trades, PF 0.70-1.06. 94% stop exits — slower is later, not better |
| atr_channel | SMA(20) +/- 1.5xATR(14) breakout | Loser: -$1,839 combined, 639 trades, PF 0.74-1.18. HYPE +$1,943 only green leg |
| envelope_trend | SMA(20) +/- 5% envelope breakout | Green but thin: +$1,524 combined, 48 trades. HYPE +$1,209 (PF 1.93) is the only leg with weight; BTC 3 trades |
| classic_pivots | Floor-trader PP/R1/S1 from prior bar | **Batch worst, structural**: -$27,883 combined, 4,476 trades, PF 0.44-0.54, drawdowns 90-97% on every coin. One-bar levels break every 3-4 bars |
| double_top_bottom | Double top/bottom, 5-bar zigzag, 1.5% tolerance | Loser: -$1,186 combined, 64 trades, PF 0.44-2.29. BTC -$1,207 does all the damage; ETH/HYPE thin |
| head_shoulders | H&S / inverse H&S, 3% shoulder tolerance | Flat: +$458 combined, 60 trades. ETH +$558 (PF 1.97) is the best small pattern leg; BTC +$36 is noise |
| triangle_breakout | Ascending/descending triangles, 1% flat side | Green but thin: +$905 combined, 81 trades. ETH +$713 (PF 2.45) on 20 trades is interesting, not significant |
| wedge_breakout | Rising/falling wedges, two-pivot trendlines | Loser: -$3,174 combined, 495 trades, PF 0.61-1.27. Two-pivot trendlines converge constantly on noisy 1h data |
| flag_pattern | Flag: >=3xATR pole + tight consolidation + breakout | Loser: -$1,500 combined, 68 trades, PF 0.29-2.74. ETH 13.6% win is the batch's worst leg |
| swing_sr_bounce | Swing S/R bounce, 2+ touches within 0.5% | **Second structural failure**: -$25,365 combined, 3,311 trades, PF 0.46-0.59, drawdowns 78-94% on every coin. Two-touch levels break more than they hold |
| macd_divergence | MACD histogram divergence (Appel/Aspray) | **Batch best**: +$1,557 combined, 244 trades. HYPE +$3,383 (42.9% win, PF 1.91, Sharpe 2.70) carries it; BTC -$1,729, ETH flat |

## Empirical direction

The honest-loser streak extends, but batch 16 splits into two distinct
stories. Story one is the two structural failures: classic_pivots and
swing_sr_bounce together lose -$53,248 — 87% of the batch's combined
loss — on 7,787 trades, because both build "levels" out of almost no
information (one bar's range, two touches) and then trade every touch
of them. Levels need memory to mean anything; without it they are just
lines price crosses constantly, and the failure exits turn the account
into a fee pump. Neither is tunable — both need a different level
definition to be a different strategy, and the prior for that working
is low. Story two is the rest: the crossover/channel family keeps
losing the same way (fast crosses churn, slow crosses confirm late),
the chart patterns split between thin greens (envelope, triangle,
head & shoulders — all under 100 trades, none significant) and
ordinary losers (double tops, wedges, flags), and exactly one
strategy earns a follow-up: macd_divergence, whose HYPE leg (+$3,383,
PF 1.91) is the strongest single leg in the batch. The follow-up is a
longer window or more coins for macd_divergence only — everything
else in this batch is either dead or too thin to matter. Nothing here
is anywhere near a live gate. Per-coin detail lives in each strategy's
BACKTEST.md / CALIBRATION.md.

## Batch 17 — 2026-10-26 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, 2026-03-14 → 2026-10-25, $10k, 0.045% fee + 0.01% slip/side, funding off)

| Slug | Mechanism | Result |
|---|---|---|
| roc_momentum | ROC(12) zero-cross | Loser: -$14,293 combined, 2,237 trades, PF 0.59-0.89 |
| volatility_breakout | Williams prior-close +/- 0.5x prior range | Structural loser: -$24,013 combined, 3,499 trades, PF 0.52-0.64 |
| volume_spike_breakout | 20-bar breakout + volume >2x avg | Near-flat loser: -$354 combined, 443 trades; ETH/HYPE green, BTC drags under |
| volatility_contraction_pattern | Minervini VCP proxy (1h): uptrend + falling ATR + tight range + breakout on volume, long only | Thin green: +$1,170 combined, 66 trades, all three legs positive — too thin to call |
| three_soldiers_crows | Nison three strong candles, inside opens | Thin loser: -$933 combined, 41 trades |
| morning_evening_star | Nison star reversal (gap adapted for 24/7 crypto) | Thin green: +$1,346 combined, 29 trades, all legs positive — too few to be a finding |
| dark_cloud_piercing | Nison dark cloud / piercing (gap adapted) | Loser: -$5,675 combined, 428 trades, loses on every coin |
| harami_pattern | Nison harami, small body inside large body | Loser: -$870 combined, 160 trades; ETH leg green (PF 1.99), BTC/HYPE red |
| tweezer_pattern | Nison tweezers, equal extremes within 0.15% | Structural loser: -$23,152 combined, 4,442 trades — equal extremes are everywhere on 1h data |
| fibonacci_extension | SMA50 trend + turn from 38.2-61.8% zone of 50-bar range | Loser: -$6,110 combined, 491 trades, win rates ~21% |
| bollinger_band_walk | First close outside BB(20,2), exit at mid-band | Flat: +$43 combined, 626 trades |
| supertrend_adx_filter | Supertrend flip gated by ADX(14)>25 | Loser: -$2,085 combined, 122 trades; the gate cuts trades but not losses |

Batch combined: -$74,926 across 12,584 trades. 98 tests green.

## Empirical direction (batch 17)

Two structural failures dominate: volatility_breakout and tweezer_pattern
together lose -$47,165 on 7,941 trades, because both fire on conditions
that are near-constant on 1h crypto bars (every bar has a prior range to
break; equal extremes occur constantly in a jittery market). The
candlestick family splits the same way as before: strict textbook
patterns either never fire in a gapless 24/7 market (the strict-gap
star and dark-cloud versions produced exactly 0 trades and had to be
adapted to open-beyond-prior-close) or, once adapted, lose steadily.
The only greens are thin by construction — VCP (+$1,170, 66 trades)
and morning star (+$1,346, 29 trades) — and neither has the trade
count to survive a significance claim. The honest read for the batch:
nothing here earns a follow-up window, and the candlestick lane on 1h
crypto looks exhausted as a source of new strategies. Per-coin detail
lives in each strategy's BACKTEST.md / CALIBRATION.md.

## Batch 18 (2026-10-27)

12 new strategies shipped, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h (BTC/ETH/HYPE, 2026-03-14 22:00 UTC →
2026-10-27 13:00 UTC, BTC/ETH 5,440 bars, HYPE 5,438). Costs: 0.045%
taker + 0.01% slippage/side, funding off. Sizing: 1% equity risk/trade
on the 2xATR stop, 3x leverage cap, $10k. 96 new unit tests green.
Combined -$57,189 across 10,232 trades.

| slug | source | result |
|---|---|---|
| ehlers_sinewave | Ehlers Even Better Sinewave (sine/lead-sine cross; causal lead approx) | **Batch worst**: -$22,962 combined, 4,089 trades, PF ~0.5-0.7. The cross fires ~8x/day/coin on 1h bars — cycle-mode theory drowned in whipsaw |
| fast_stochastic | Lane Fast Stochastic %K(14)/%D(3), cross in 20/80 zones | Loser: -$10,930 combined, 1,078 trades. Removing %K smoothing makes slow_stochastic's failure worse, not better |
| bollinger_bandwidth | BB(20,2) bandwidth expansion breakout, exit at mid-band | Loser: -$2,539 combined, 333 trades. Expansion filter does not save the band breakout; HYPE +$661 only green leg |
| rsi_trendline | RSI(14) trendline break (confirmed 3-bar pivots) | Loser: -$7,390 combined, 1,136 trades. Breaks mark pauses, not reversals |
| elder_thermometer | Elder Market Thermometer (range < 60% of 20-bar avg + trend-side close) | Loser: -$10,114 combined, 841 trades. Quiet prints are continuation pauses as often as reversals |
| volume_oscillator | Volume Oscillator (5/10) zero-cross + SMA20 trend filter | Flat: +$10 combined, 846 trades, expectancy $0.01/trade. No directional edge at 1h |
| relative_momentum_index | Altman RMI(20,5), 50-midline cross; RMI(14,1)==RSI asserted in tests | Flat: +$346 combined, 670 trades. Smoother RSI, same non-edge |
| hammer_pattern | Nison hammer / shooting star (trend + body-position rules) | Loser: -$2,191 combined, 427 trades. Stricter than pin_bar_reversal, same outcome |
| doji_reversal | Nison doji at 10-bar extreme after 3-bar trend | Loser: -$648 combined, 398 trades. ETH +$2,201 (Sharpe 1.81) is the batch's best leg, BTC drags it under |
| marubozu_breakout | Nison marubozu (body >= 90% of range) conviction candle | Loser: -$1,138 combined, 399 trades. Conviction candles continue as often as they reverse |
| three_methods_pattern | Nison rising/falling three methods (5-bar containment) | Inconclusive: +$452 on 13 trades. Too strict to evaluate on 1h |
| bat_pattern | Carney Bat (2001): AB 38.2-50%, CD 161.8-261.8%, AD 88.6% ±6% | Inconclusive: -$86 on 2 trades (0 on HYPE). Harmonic completeness is a daily-chart property, as with Gartley |

| macd_zero_cross | Appel MACD(12,26,9) zero-line cross | Loser: -$1,222 combined, 572 trades. HYPE +$760 only green leg |
| ppo_cross | Percentage Price Oscillator signal cross | Loser: -$7,752 combined, 1,221 trades. Normalising MACD by price fixes nothing |
| keltner_rsi | Keltner breakout + RSI(14) band filter | Loser: -$5,665 combined, 660 trades, worst expectancy -$8.58/trade in its group |
| rsi_macd_combo | RSI 50-cross + MACD histogram confluence | Loser: -$5,940 combined, 1,039 trades. ETH win rate 19.4% |
| adx_macd_trend | ADX(14)>25 + MACD signal cross | Loser: -$3,331 combined, 188 trades. ADX filter does not save the MACD cross |
| heikin_ashi_smoothed | Smoothed Heikin-Ashi trend flips | **Batch worst**: -$17,167 combined, 2,235 trades, fees $11,985. No flat state — chop traded continuously |
| cypher_pattern | Carney Cypher harmonic (78.6% XC completion) | Inconclusive: -$167 on 8 trades. Tolerances not loosened; pattern barely occurs at 1h |
| pennant_pattern | Pennant pole + converging-range breakout | Flat-to-loser: -$159 on 24 trades. Thin sample, HYPE leg -$326 |
| rectangle_breakout | Rectangle range breakout + volume confirm | Loser: -$1,266 combined, 229 trades. ETH +$1,004 only green leg |
| triple_top_bottom | Triple top/bottom neckline break | Loser: -$1,006 combined, 130 trades. Loses on all three coins |
| diamond_pattern | Diamond expand-then-contract breakout | Loser: -$376 combined, 97 trades. Smallest loss; ETH +$934 (PF 1.57) vs HYPE -$1,161 |
| cci_divergence | Lambert CCI(20) pivot divergence | Loser: -$962 combined, 156 trades. ETH/HYPE green, BTC -$1,908 drags it under |

## Empirical direction (batch 18)

The honest-loser streak holds for a twelfth batch: 8 of 12 lose
outright, 2 are flat to the dollar, and 2 never fire enough to judge.
The batch's through-line is that *every* remaining classic lane now
fails the same way: the oscillator lane (SineWave, fast stochastic,
RSI trendline, RMI) loses on cross frequency, the candle lane
(hammer, doji, marubozu) loses on location-without-structure, and the
pattern lane (three methods, Bat) does not fire at all. The two flat
prints (volume_oscillator +$10, relative_momentum_index +$346) are
the interesting non-results: both are verified implementations
(RMI(14,1)==RSI is a unit test) of respected mechanisms that simply
have no edge on hourly crypto — the library's null results are now
as well-identified as its losers. Nothing here is anywhere near a
live gate. Per-coin detail lives in each strategy's BACKTEST.md /
CALIBRATION.md.

## Empirical direction (batch 19)

The honest-loser streak holds for a thirteenth batch: 10 of 12 lose
outright, 1 is flat-to-loser on 24 trades, and 1 never fires enough
to judge (8 trades). Combined -$45,013 across 6,559 trades; nothing
here is anywhere near a live gate. The batch's through-line is that
the confluence idea fails the same way the single-indicator idea
did: adding a filter (ADX, RSI band, RSI+MACD agreement) delays
entries into moves already underway without cutting the whipsaw —
keltner_rsi, rsi_macd_combo and adx_macd_trend all lose on every
coin. The pattern lane splits cleanly: the strict harmonics and
chart patterns (Cypher, pennant) barely fire at 1h, while the ones
that do fire (rectangle, triple top/bottom, diamond) lose small
because their breakouts mean-revert. The batch's worst print,
heikin_ashi_smoothed (-$17,167, fees $11,985), is a structural
lesson: a flip-on-every-cross system with no flat state pays full
fees through chop. Per-coin detail lives in each strategy's
BACKTEST.md / CALIBRATION.md.

## Batch 20 — 2026-10-29 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)

12 new strategies shipped, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h. Window: 2026-03-14 22:00 UTC →
2026-10-28 00:00 UTC for nine strategies (BTC/ETH 5,451 bars after
dedup, HYPE 5,449); the three builder-C strategies (ema_triple_cross,
relative_strength_breakout, abandoned_baby_pattern) were run before a
mid-batch cache extension and cover → 2026-10-27 13:00 UTC (BTC/ETH
5,445 bars, HYPE 5,443). Costs: 0.045% taker + 0.01% slippage/side.
Sizing: 1% equity risk/trade, 3x leverage cap, $10k. 118 new unit tests
green. Combined -$66,502 across 6,963 trades.

| slug | source | result |
|---|---|---|
| macd_bollinger | Bollinger Bands on the MACD line (Carter-style band-edge / squeeze release) | Loser: -$5,711 combined, 417 trades. Loses on all three coins |
| cci_zero_cross | Lambert CCI(20) zero-line cross + SMA(50) trend filter | Loser: -$9,926 combined, 920 trades. Worst leg BTC -$4,217 |
| macd_histogram_reversal | Elder MACD-histogram slope-flip (histogram tick reversal) | **Batch worst**: -$18,600 combined, 1,844 trades. Fires on nearly every local wiggle |
| rsi_failure_swing | Cardwell RSI failure swings (RSI breaks its own prior swing) | Loser: -$2,310 combined, 100 trades. 94/100 exits are stops |
| stochastic_pop | Raschke Stochastic Pop (fast-%K cross + 20-bar breakout) | Loser: -$2,189 combined, 373 trades. Fees $3,946 exceed the loss — churn, not edge |
| keltner_pullback | Keltner midline pullback in an EMA50 trend | Loser: -$11,461 combined, 1,253 trades. 865/1,253 exits are opposite-cross whipsaws |
| ema_triple_cross | 3-EMA (3/8/21) stack alignment | Loser: -$11,917 combined, 1,451 trades. Exit churns on EMA wobble (971 signal exits) |
| relative_strength_breakout | Coin/BTC ratio-line breakout of prior 20-bar range | Loser: -$3,610 combined, 531 traded-leg trades. BTC is the benchmark (0 trades, excluded) |
| abandoned_baby_pattern | Nison abandoned baby (gap, doji, gap reversal) | No-trade: 0 trades on all coins. 24/7 crypto has essentially no true inter-bar gaps at 1h — untradeable as specified |
| kicker_pattern | Nison kicker (gap + strong opposite candle) | No evidence: -$76 on 5 trades. Textbook gap test nearly impossible at 1h |
| tasuki_gap_pattern | Nison tasuki gap continuation (adapted retracement bound — see BACKTEST.md) | Mildly green, not a win: +$238 on 42 trades, 39/42 exits are stops. Literal textbook rule fires 0 times in ~16,300 bars |
| counterattack_lines | Nison counterattack lines (close within 0.2xATR of prior close) | Loser: -$940 combined, 27 trades. BTC 0-for-8; a stalemate candle reads as a pause, not a turn |

## Empirical direction (batch 20)

The honest-loser streak holds for a fourteenth batch: 9 of 12 lose
outright, 1 is mildly green on noise (tasuki +$238 on $30k), and 2
never fire enough to judge (abandoned baby 0 trades, kicker 5).
Combined -$66,502 across 6,963 trades; nothing here is anywhere near
a live gate. The batch's through-line is that the candle-pattern lane
hits a structural wall on 24/7 hourly crypto: the textbook patterns
that assume an overnight close (abandoned baby, kicker, literal
tasuki) barely occur, and the adapted tasuki that does fire still
loses on stops. The oscillator lane keeps failing on frequency:
histogram reversal (1,844 trades) and EMA-stack flips (1,451) pay
their edge away in fees and whipsaw exits, and the pullback lane
(keltner_pullback) whipsaws on the opposite cross 69% of the time.
Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.

## Batch 21 — 2026-10-30 (12 built, 10 merged, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)

12 new strategies built, each: indicators + signals + risk config + unit
tests + backtest on Hyperliquid 1h. Window: 2026-03-14 22:00 UTC →
2026-10-30 00:00 UTC (BTC/ETH 5,499 bars after dedup, HYPE 5,497).
Costs: 0.045% taker + 0.01% slippage/side. Sizing: 1% equity risk/trade,
3x leverage cap, $10k. 132 new unit tests green across the 12 builds.

MERGE NOTE: anchored_vwap and liquidity_sweep already existed on main
(first shipped in earlier windows — anchored_vwap backtested →2026-10-15,
liquidity_sweep →2026-10-17). Per the first-shipped rule their batch-21
builds were NOT merged; main keeps the earlier versions. The 10 merged
strategies total 111 tests and combined -$38,957 across 6,480 trades.
All 12 builds' backtest figures are recorded below for the record; the
two DUPLICATE rows describe builds that were not merged.

| slug | source | result |
|---|---|---|
| anchored_vwap | Brian Shannon anchored VWAP (pivot-anchored, Investopedia) | DUPLICATE — not merged; first-shipped version kept. Batch-21 build: -$5,543 combined, 525 trades, win rate 19.8% |
| vwap_std_bands | Session VWAP ±1σ/2σ bands (StockCharts VWAP) | Loser: -$8,103 combined, 695 trades. Loses on all three coins despite a 48.9% win rate — losers run larger than winners |
| order_flow_imbalance | Bar-delta footprint proxy (cumulative-delta concept, NordFX explainer) | Loser: -$10,996 combined, 1,424 trades. The OHLCV delta proxy carries no directional information at 1h |
| structure_break_bos | Market-structure BOS/CHoCH (swing-pivot breaks) | Flat: +$283 combined, 433 trades. HYPE +$2,203 carries BTC/ETH losses — noise, not an edge |
| liquidity_sweep | Sweep of prior 20-bar extreme + reclaim (SMC) | DUPLICATE — not merged; first-shipped version kept. Batch-21 build: -$4,761 combined, 516 trades |
| asian_range_breakout | Asian session (00:00–08:00 UTC) range breakout | Loser: -$1,186 combined, 500 trades. ETH +$1,488 only green leg; the session edge does not survive 24/7 crypto |
| point_and_figure | Dorsey P&F, 1% box, 3-box reversal | Loser: -$1,581 combined, 186 trades. Loses on all three coins; 174/186 exits are stops |
| poc_migration | Rolling 50-bar volume-profile POC trend | Loser: -$10,319 combined, 1,387 trades. The rolling POC flips constantly (~1 trade per 12 bars); fees $8,946 nearly equal the loss |
| multi_timeframe_stack | 4h EMA trend + 1h EMA(9/21) cross confluence | Mildly green, not a win: +$1,161 combined, 333 trades, profit factors 1.03–1.15, 78% of exits are stops — breakeven noise |
| dmi_cross | Wilder +DI/-DI cross with ADX(14)>20 filter (StockCharts ADX) | Loser: -$4,709 combined, 552 trades. Loses on all three coins; 303/552 exits are stops |
| aroon_cross | Chande Aroon(25) cross with >70 strength gate (StockCharts Aroon) | Flat: +$119 combined, 588 trades. BTC loses, ETH/HYPE small greens — no edge |
| money_flow_index | MFI(14) oversold/overbought recovery (StockCharts MFI) | Loser: -$3,626 combined, 382 trades. Loses on all three coins, profit factor 0.77–0.80 |

## Empirical direction (batch 21)

The honest-loser streak holds for a fifteenth batch: of the 10 merged
strategies, 7 lose outright and 3 are flat-to-noise (structure_break_bos
+$283, aroon_cross +$119, multi_timeframe_stack +$1,161 on $30k); none is
anywhere near a live gate. The batch's through-line is that the
volume/structure lane fails the same way the oscillator and candle lanes
did: VWAP bands lose on every coin, the bar-delta order-flow proxy is a
heavy loser, and the rolling-POC trend overtrades itself into fees. The
multi-timeframe idea (4h trend gating 1h entries) is the batch's only
mildly green merged print and still cannot clear breakeven once stops
dominate 78% of exits. A process note: the local worktree was stale
relative to main (missing ~50 strategy dirs already on main), which is
how anchored_vwap and liquidity_sweep were rebuilt as duplicates; future
batches must diff candidate slugs against main's tree, not just the
worktree listing. Per-coin detail lives in each strategy's BACKTEST.md /
CALIBRATION.md (merged strategies only; the two duplicate builds' docs
live on the unmerged batch branch).

## Batch 22 — 2026-10-31 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)

| hull_ma_cross | HMA(16)/HMA(64) cross (Alan Hull) | Flat: +$166 combined, 878 trades, PF 1.00 — HYPE +$3,726 offsets BTC/ETH losses, breakeven noise |
| woodie_pivots | Woodie daily pivots, R1/S1 breakout, PP exit | Loser: -$927 combined, 397 trades, 86% of exits are stops |
| linear_regression_channel | Raff regression channel mean reversion (50-bar, 2σ) | Loser: -$3,513 combined, 492 trades, loses on all three coins despite a 44.9% win rate |
| halftrend | Everget HalfTrend trend flips (amplitude 2, ATR(100) channels) | Loser: -$2,518 combined, 741 trades; HYPE +$1,760 only green leg |
| frama_trend | Ehlers FRAMA(16) price cross | Loser: -$19,837 combined, 3,066 trades — FRAMA hugs price and whipsaws |
| vidya_trend | Chande VIDYA (CMO(9), EMA 20) price cross | Loser: -$10,518 combined, 1,303 trades, loses on all three coins |
| choppiness_index | Choppiness(14) < 38.2 + Donchian(20) breakout | Loser: -$2,029 combined, 187 trades; HYPE +$255 only green leg (noise) |
| efficiency_ratio | Kaufman ER(10) > 0.3 gating EMA(9/21) cross | Mildly green, not an edge: +$1,596 combined, 364 trades, PF 1.09, BTC leg -$2,074 |
| chande_momentum_osc | CMO(14) ±50/0 threshold crossings | Loser: -$4,419 combined, 413 trades, loses on all three coins |
| chaikin_money_flow | CMF(20) zero cross | Loser: -$14,061 combined, 1,900 trades, loses on all three coins |
| wyckoff_upthrust | Wyckoff upthrust shorts (20-bar range, short-only) | Loser: -$2,374 combined, 417 trades — least-bad of the batch |
| wilder_accumulative_swing | Wilder ASI cross of its EMA(10) | Loser: -$21,263 combined, 3,299 trades — worst of the batch |

## Empirical direction (batch 22)

The honest-loser streak holds for a sixteenth batch: of the 12 merged
strategies, 10 lose outright and 2 are flat-to-noise (hull_ma_cross +$166,
efficiency_ratio +$1,596 on $30k); none is anywhere near a live gate. The
batch's through-line is that the adaptive-average lane fails by whipsaw
(FRAMA and VIDYA both hug price and churn ~1,000+ trades per coin into
fees) while the volume-price lane fails by overtrading (CMF and ASI
combine for -$35,324 across 5,199 trades). The two near-breakeven prints
are both trend-cross variants whose green legs (HYPE for Hull, ETH/HYPE
for ER-gated EMA) do not survive the other coins. Combined batch print:
-$79,697 across 13,457 trades. Per-coin detail lives in each strategy's
BACKTEST.md / CALIBRATION.md. Process note: all 12 slugs were diffed
against main's live tree via the API before building, so no duplicate
rebuilds this batch — the stale-worktree trap from batch 21 is closed.

## Batch 23 — 2026-11-01 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)

Window t in [1773525600000, 1793538000000] (2026-03-14 22:00 UTC →
2026-11-01 13:00 UTC): local cache extended with the public
candleSnapshot tail to the last completed hour bar; the cache file
itself was not rewritten. All 12 slugs were diffed against main's live
tree via the API before building — six candidates already on main
(mass_index, williams_pct_r, opening_range_breakout, camarilla_pivots,
connors_rsi, inside_bar_breakout) were dropped, not rebuilt.

| guppy_mma | GMMA 12-EMA ribbon cross (Guppy) | Flat: +$2 combined, 582 trades, PF 1.00 — HYPE green leg offsets BTC/ETH losses, breakeven noise |
| dpo_cross | DPO(20) zero cross (displaced SMA) | Loser: -$8,977 combined, 1,267 trades, loses on all three coins |
| rvi_cross | Ehlers RVI vs signal cross | Loser: -$20,988 combined, 3,010 trades — second-worst of the batch, oscillator whipsaw |
| fvg_mitigation | SMC fair value gap first-mitigation entries | Mildly green, not an edge: +$1,173 combined, 696 trades, PF 1.03, green only on HYPE |
| zscore_reversion | Bollinger z-score ±2 entry, 0 exit | Loser: -$11,515 combined, 829 trades, loses on all three coins |
| rsi_bollinger_bands | Bollinger bands on RSI(14) | Loser: -$10,744 combined, 789 trades, loses on all three coins |
| central_pivot_range | Ochoa CPR TC/BC breakout (prior UTC day) | Loser: -$5,973 combined, 1,103 trades; HYPE green leg only |
| nr7_breakout | Crabel NR7 range breakout (24-bar validity) | Loser: -$18,252 combined, 2,177 trades — daily pattern diluted on 1h bars |
| inverse_fisher_rsi | Ehlers IFish on RSI(5), ±0.5 thresholds | Loser: -$3,590 combined, 1,005 trades — least-bad loser of the batch |
| cg_oscillator | Ehlers CG vs trigger cross | Loser: -$20,629 combined, 3,362 trades — worst of the batch, 10-bar centroid flips constantly |
| negative_volume_index | Dysart/Fosback NVI vs EMA(255) | Loser: -$7,702 combined, 552 trades, loses on all three coins |
| volume_price_trend | PVT vs SMA(20) cross | Loser: -$8,719 combined, 1,332 trades, loses on all three coins |

## Empirical direction (batch 23)

The honest-loser streak holds for a seventeenth batch: of the 12
strategies, 10 lose outright and 2 are flat-to-noise (guppy_mma +$2,
fvg_mitigation +$1,173 on $30k); none is anywhere near a live gate.
The batch's through-line is that the oscillator lane fails by
overtrading (RVI and CG combine for -$41,617 across 6,372 trades,
both with MaxDD beyond -70% on the combined curve) while the
mean-reversion lane fails by fading trends (z-score, RSI bands, and
IFish all lose on all three coins or all but HYPE). The two
near-breakeven prints are both trend-ribbon/gap variants whose green
legs are HYPE-only and do not survive BTC or ETH. Combined batch
print: -$115,913 across 16,704 trades. Per-coin detail lives in each
strategy's BACKTEST.md / CALIBRATION.md. Process note: all 12 slugs
were diffed against main's live tree via the API before building, so
no duplicate rebuilds this batch — the stale-worktree trap from batch
21 stays closed.

## Batch 24 — 2026-11-02 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)
Window t in [1773525600000, 1793628000000] (2026-03-14 22:00 UTC →
2026-11-02 14:00 UTC): local cache extended with the public
candleSnapshot tail to the last completed hour bar; the cache file
itself was not committed. All 12 slugs were diffed against main's live
tree via the API before building — four candidates already on main
(qstick, tdi, momentum_pinball, and the lsma_slope-adjacent linreg idea)
were dropped, not rebuilt.
| aroon_oscillator | Chande Aroon oscillator (25) zero cross | Loser: $-1,954 combined, 750 trades, PF 0.94 — green only on ETH |
| gann_hilo | Krausz Hi-Lo Activator SMA(3) state flips | Loser: $-18,135 combined, 2391 trades, PF 0.68 — loses on all three coins, worst of the batch |
| hull_suite | InSilico Hull Suite HMA(16) slope turns | Loser: $-17,050 combined, 2160 trades, PF 0.70 — loses on all three coins, second-worst of the batch |
| kumo_breakout | Ichimoku Kumo cloud-edge breakout | Loser: $-9,118 combined, 896 trades, PF 0.69 — loses on all three coins |
| obv_cross | OBV vs EMA(20) cross (Granville) | Loser: $-16,198 combined, 2102 trades, PF 0.67 — loses on all three coins, BTC win rate just 19.4% |
| ravi | Chande RAVI +/-0.3% reference lines | Loser: $-1,681 combined, 409 trades, PF 0.92 — loses on all three coins, second-smallest loss |
| vhf | White VHF(28) regime trigger + SMA direction | Loser: $-4,366 combined, 415 trades, PF 0.76 — green only on HYPE |
| zigzag_swing | ZigZag 5% confirmed-swing breakout | Loser: $-1,048 combined, 175 trades, PF 0.88 — loses on all three coins, smallest loss of the batch |
| gann_fan | Gann 1x1 fan at 1 ATR/bar from 30-bar anchors | Loser: $-9,657 combined, 1067 trades, PF 0.79 — loses on all three coins |
| keltner_breakout | Keltner EMA(20) +/- 2xATR(10) breakout | Loser: $-2,892 combined, 417 trades, PF 0.85 — loses on all three coins |
| adaptive_rsi | Kaufman ER-adaptive RSI(14), 30/70 entries | Loser: $-1,728 combined, 91 trades, PF 0.62 — loses on all three coins on only 91 trades |
| kijun_cross | Ichimoku Kijun-sen(26) cross alone | Loser: $-10,375 combined, 1552 trades, PF 0.79 — loses on all three coins |

## Empirical direction (batch 24)

The honest-loser streak holds for an eighteenth batch: all 12
strategies lose outright, none green on more than one coin, none
anywhere near a live gate. Combined batch print: -$94,202 across
12,425 trades. The through-line splits two ways: the fast
state/turn/flow lane fails by overtrading (gann_hilo, hull_suite,
and obv_cross combine for -$51,383 across 6,653 trades, all with
combined MaxDD beyond -55%), while the slow regime/level lane fails
by arriving late (kumo, kijun, and keltner_breakout lose on every
coin despite far fewer trades). The least-bad print is zigzag_swing
at -$1,048 on just 175 trades — near-flat, but still negative
everywhere and too thin to be a signal. Per-coin detail lives in
each strategy's BACKTEST.md / CALIBRATION.md. Process note: all 12
slugs were diffed against main's live tree via the API before
building, so no duplicate rebuilds this batch.

## Batch 25 — 2026-11-03 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)
Window t in [1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC): local cache extended with the public
candleSnapshot tail to the last completed hour bar; the cache file
itself was not committed. All 12 slugs were diffed against main's live
tree via the API before building — no duplicate rebuilds this batch.
| trend_intensity_index | Pee TII(30) 80/20 crosses | Winner: +$1,468 combined, 27 trades, PF 2.37 — green on all three coins, but only 27 trades: a thin low-frequency print, not a live gate |
| relative_volatility_index | Dorsey RVI(10/10) 50 cross | Loser: $-20,273 combined, 3154 trades, PF 0.66 — worst of the batch, overtrades into noise |
| kairi_index | Kairi (close-SMA25)/SMA25, +/-5% recovery | Loser: $-1,913 combined, 78 trades, PF 0.50 — loses on all three coins |
| pring_special_k | Pring Special K vs its signal line | Mixed: +$542 combined, 934 trades, PF 1.01 — HYPE +$3,805 carries BTC/ETH losses |
| blau_dss | Blau DSS(21,3,3) vs trigger | Loser: $-19,145 combined, 2676 trades, PF 0.69 — second-worst, overtrades |
| cutler_rsi | Cutler simple-average RSI(14) 30/70 | Loser: $-6,713 combined, 780 trades, PF 0.81 — loses on all three coins |
| cardwell_rsi_ranges | Cardwell RSI bull 40-80 / bear 20-60 ranges | Loser: $-1,872 combined, 393 trades, PF 0.90 — BTC near breakeven (-$68), still negative everywhere |
| fibonacci_fan | Rolling 50-bar Fibonacci fan lines | Loser: $-2,103 combined, 440 trades, PF 0.90 — green only on HYPE |
| fibonacci_pivots | Prior-24-bar Fibonacci pivots (R1/S1) | Loser: $-3,946 combined, 632 trades, PF 0.86 — loses on all three coins |
| demark_trendline | DeMark TD trendline breakouts (2-bar pivot lag) | Loser: $-13,118 combined, 1601 trades, PF 0.76 — BTC/ETH MaxDD ~-59% |
| weinstein_stage | Weinstein Stage 2/4 via EMA150/200 | Loser: $-1,169 combined, 476 trades, PF 0.94 — green on ETH/HYPE, BTC drags it negative |
| wyckoff_sos | Wyckoff SOS/SOW, 40-bar range + 1.5x volume | Loser: $-5,358 combined, 576 trades, PF 0.60 — loses on all three coins |

## Empirical direction (batch 25)

The honest-loser streak breaks in form but not in substance: two
combined-green prints appear for the first time in several batches —
trend_intensity_index (+$1,468, green everywhere) and pring_special_k
(+$542, HYPE-carried) — but neither clears a live gate. TII's edge
rests on 27 trades in 7.5 months, far too thin to trust, and Pring's
combined green masks two losing coins. The rest of the batch repeats
the established pattern: the fast cross/oscillator lane fails by
overtrading (RVI, Blau DSS and DeMark combine for -$52,535 across
7,431 trades, all with combined MaxDD beyond -46%), while the slow
level/range lane fails quietly (Fibonacci pivots, Cardwell ranges and
Kairi all lose on every coin at PF 0.50-0.90). Combined batch print:
-$73,599 across 11,767 trades. Per-coin detail lives in each
strategy's BACKTEST.md / CALIBRATION.md. Process note: all 12 slugs
were diffed against main's live tree via the API before building, so
no duplicate rebuilds this batch.

## Batch 26 — 2026-11-04 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)
Window t in [1773525600000, 1793800800000] (2026-03-14 22:00 UTC →
2026-11-04 14:00 UTC): local cache extended with the public
candleSnapshot tail to the last completed hour bar; the cache file
itself was not committed. All 12 slugs were diffed against main's live
tree via the API before building — no duplicate rebuilds this batch.
| elliott_wave_oscillator | Williams EWO(5/35) zero cross + SMA50 slope | Loser: $-2,073 combined, 376 trades, PF 0.74-1.02 — green only on HYPE, wins <30% on BTC/ETH |
| acceleration_bands | Headley bands (20, factor 4), 2 closes outside | Loser: $-5,015 combined, 379 trades, PF 0.48-0.81 — loses on all three coins |
| rainbow_ma | 22-EMA ribbon (9-100) breakout | Loser: $-14,000 combined, 1860 trades, PF 0.59-0.82 — worst of the batch, MaxDD -46.7% |
| percentage_volume_osc | PVO(12,26,9) signal crosses + SMA50 filter | Loser: $-6,239 combined, 1225 trades, PF 0.67-0.93 — loses on all three coins |
| harmonic_butterfly | Butterfly XABCD (B 0.786, D 1.272 XA) | Loser: $-163 combined, 13 trades, PF 0.34-1.04 — thin, fires rarely |
| harmonic_crab | Crab XABCD (B 0.382-0.618, D 1.618 XA) | Near-no-signal: $-146 combined, 2 trades, both on BTC — band too strict for 1h crypto |
| harmonic_shark | Shark XABCD (C 1.13-1.618 AB, D 0.886-1.13 XA) | Marginal green: +$269 combined, 26 trades, PF 0.86-2.16 — only combined-green print, thin, BTC-only |
| episodic_pivot | Bonde/Qullamaggie EP, 1h adaptation (gap >=2%, vol >=3x) | No trades: port failure — 1h crypto has no session gaps (max observed gap 1.43%), trigger can never fire |
| gap_and_go | Gap >=1.5% on >=2x volume, break of gap-bar extreme | No trades: same structural port failure — no 1h bar gaps >=1.5% in the window |
| outside_bar_breakout | Engulfing-range bar, break of its extreme | Loser: $-1,575 combined, 427 trades, PF 0.47-1.34 — HYPE +$2,262 carried, BTC -$3,478 drags it negative |
| stoch_macd_combo | Stoch(14,3) 30/70 cross + MACD confirmation | Loser: $-1,072 combined, 67 trades, PF 0.33-0.81 — loses on all three coins |
| keltner_macd | Keltner(20,10,1.5) breakout + MACD confirmation | Loser: $-8,226 combined, 706 trades, PF 0.67-0.89 — loses on all three coins |

## Empirical direction (batch 26)

The honest-loser streak holds: 10 of 12 strategies lose combined, one
is marginally green on 26 thin trades (harmonic_shark, +$269, BTC-only),
and two print zero trades for a structural reason, not a code reason.
The batch's real finding is the port failure: session-gap setups
(episodic_pivot, gap_and_go) cannot trigger on continuous 1h crypto
candles at all — max hourly gap in the window is 1.43% (HYPE), below
both thresholds — so gap-based equity setups need session-based data
to be testable, and should not be re-ported to 1h bars. Elsewhere the
established pattern repeats: band/ribbon breakouts fail by overtrading
(rainbow_ma -$14,000 on 1,860 trades, keltner_macd -$8,226 on 706),
oscillator crosses fail quietly (PVO, stoch+MACD, EWO all PF < 1.0
combined), and harmonic patterns mostly do not fire (crab: 2 trades;
butterfly: 13). Combined batch print: -$38,242 across 5,081 trades.
Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via
the API before building, so no duplicate rebuilds this batch.

## Batch 27 — 2026-11-05 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)
Window t in [1773525600000, 1793887200000] (2026-03-14 22:00 UTC →
2026-11-05 14:00 UTC): local cache extended with the public
candleSnapshot tail to the last completed hour bar; the cache file
itself was not committed. 5 of the 12 candidate slugs were already on
main (supertrend, guppy_mma, williams_alligator, parabolic_sar,
ttm_squeeze) and were swapped for alternates (kama, zlema,
vwma_crossover, mean_reversion_zscore, adx_trend_system) after a live
API diff — no duplicate rebuilds this batch.
| turtle_trading | Turtle System 1 (20/10) + System 2 (55/20) breakouts, 2N stop | Loser: $-3,069 combined, 633 trades, PF 0.77-1.02 — ETH +$191 breakeven noise, BTC/HYPE lose, 89% of exits are stops |
| ichimoku_cloud | Tenkan/Kijun cross + price vs cloud + Chikou confirmation | Loser: $-1,654 combined, 187 trades, PF 0.67-0.99 — strictest filters in the batch, worst combined win rate (29.9%) |
| heikin_ashi_trend | 2 same-colour HA candles + EMA50 filter, exit on first opposite colour | Loser: $-22,064 combined, 2480 trades, PF 0.44-0.66 — churns to death, $11,102 in fees |
| donchian_channel | Donchian 20-bar breakout, exit through midline | Loser: $-3,116 combined, 663 trades, PF 0.75-1.00 — ETH flat (+$17), BTC/HYPE lose, 79% of exits are stops |
| elder_impulse_system | EMA13 + MACD-hist impulse bars (green/red/blue) | Loser: $-23,143 combined, 3711 trades, PF 0.51-0.60 — worst churn of the batch, $15,462 in fees; Elder built it as a filter, not an entry trigger |
| hull_ma_crossover | HMA(16) vs HMA(32) cross + slope filter | Loser: $-5,383 combined, 1288 trades, PF 0.76-1.06 — HYPE alone green (+$1,060), Hull's anti-crossover warning holds |
| williams_r_oscillator | %R(14) exit-the-extreme + SMA50 filter | Loser: $-6,493 combined, 402 trades, PF 0.44-0.78 — worst per-trade expectancy in the batch (-$16.15) |
| kama | KAMA(10,2,30) price cross + rising/falling KAMA | Big loser: $-15,350 combined, 2351 trades, PF 0.60-0.79 — 22.4% win rate, $13,310 in fees |
| zlema | ZLEMA(20) vs ZLEMA(50) cross | Loser, near breakeven: $-2,151 combined, 831 trades, PF 0.82-1.12 — HYPE green (+$1,703), closest to break-even in the batch |
| vwma_crossover | VWMA(10) vs VWMA(50) cross | Breakeven scratch: $-150 combined, 562 trades, PF 0.68-1.21 — ETH +$1,857 and HYPE +$728 green, BTC -$2,736 gives it all back |
| mean_reversion_zscore | z-score vs SMA20, enter on reversion inside ±2, exit at 0 | Loser: $-2,890 combined, 323 trades, PF 0.72-0.87 — 52.9% win rate but negative expectancy; exits cut winners, stops let losers run |
| adx_trend_system | +DI/-DI cross with ADX(14) > 25 | Loser: $-2,665 combined, 261 trades, PF 0.57-0.88 — DI crosses arrive late, 28.0% win rate |

## Empirical direction (batch 27)

The honest-loser streak extends to 11 of 12 losers and one breakeven
scratch (vwma_crossover, -$150 on 562 trades) — no strategy prints
green combined, the first batch with zero combined winners. It is also
the worst batch by total dollars: -$88,128 across 13,692 trades, driven
by churn: elder_impulse_system (-$23,143 on 3,711 trades) and
heikin_ashi_trend (-$22,064 on 2,480 trades) both exit on the first
opposite-colour/impulse bar, so fees alone ($15,462 and $11,102) eat
more than half of each loss. The pattern is now structural: any system
whose exit is "first sign of weakening" (HA colour flip, impulse-blue
bar) trades itself to death on 1h crypto; any system whose entry is a
cross of two smoothed lines (KAMA, HMA, ZLEMA, VWMA) whipsaws in chop
with PF 0.60-1.12. The only near-misses are the volume-weighted and
de-lagged variants (vwma PF 0.99, zlema PF 0.94) — both still net
negative. Combined batch print: -$88,128 across 13,692 trades.
Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via
the API before building; 5 duplicates were swapped for alternates.
Backtest numbers were re-run by the coordinator on the final shipped
code and the BACKTEST.md files corrected to the verified figures
(builders' pre-fix runs differed by <0.5% of trades).

## Batch 28 — 2026-11-06 (12 strategies, Hyperliquid 1h BTC/ETH/HYPE, $10k, 0.045% fee + 0.01% slip/side, funding off)
Window t in [1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC): local cache extended with the public
candleSnapshot tail to the last completed hour bar; the cache file
itself was not committed. All 12 slugs were diffed against main's live
tree via the API before building — none existed on main (319 dirs).
| wilder_volatility_stop | Wilder Volatility System (1978): SIC ± 3x ATR(7) stop-and-reverse | Breakeven scratch: $-0.75 combined, 518 trades, PF 1.00 — HYPE +$894, BTC/ETH lose; 96% of exits are stops |
| ema_pullback | EMA(20) pullback-touch + close-back-above confirmation, EMA(50) trend filter | Worst in batch: $-18,418 combined, 1951 trades, PF 0.65 — 22.0% win rate on all three coins, -$62.0% combined MaxDD; pullback entries fire constantly into chop |
| stochastic_divergence | Slow stoch %K(14,3) regular + hidden divergence vs 5-bar pivots | Loser: $-4,160 combined, 747 trades, PF 0.86 — best win rate in the batch (47.1%) but losers outweigh winners; only HYPE green (+$248, noise) |
| wolfe_wave | Bill Wolfe 5-point wave, entry on close back above the 1-3 line, EPA 1-4 line target | Loser: $-2,075 combined, 163 trades, PF 0.74 — BTC the only green coin (+$296); ETH drives the loss |
| three_drives_pattern | Three Drives harmonic (0.618/0.786 pullbacks, 1.272/1.618 extensions, symmetry-gated) | Zero trades: $0.00 — the full pattern never completed; 5 near-misses all failed the drive-length symmetry check. Untestable as specified |
| five_zero_pattern | Carney 5-0 harmonic (AB 1.13-1.618x XA, BC 1.618-2.24x AB, D = 50% of BC) | Thin winner: +$61.57 combined, 38 trades, PF 1.09 — 65.8% win rate, +$1.62/trade expectancy; more noise than edge |
| megaphone_pattern | Broadening formation: 3 higher highs + 3 lower lows, breakout of the expanding boundary | Zero trades: $0.00 — the full pattern never completed; 9 alternating sequences on BTC failed the 0.5x ATR per-swing expansion bar. Untestable as specified |
| rounding_bottom | 60-bar saucer, neckline breakout + volume confirmation (rounding-top mirror for shorts) | Loser: $-10,429.62 combined, 490 trades, PF 0.50 — all three coins lose, 23.7% win rate, 72% of exits are stops |
| belt_hold_pattern | Nison belt hold (open on the extreme, body >= 60% of range) with trend context | Loser: $-1,184.82 combined, 556 trades, PF 0.95 — ETH wins (+$1,297) but BTC (-$2,316) gives it back; effectively breakeven-to-negative |
| shooting_star_pattern | Shooting star (short) / inverted hammer (long), upper/lower shadow >= 2x body | Breakeven scratch: +$12.45 combined, 120 trades, PF 1.00 — HYPE +$473 offset by BTC/ETH losses; noise around zero |
| volume_weighted_macd | MACD(12,26,9) on 20-bar volume-weighted price + SMA(50) trend filter | Loser: $-1,168.99 combined, 201 trades, PF 0.88 — BTC 19.1% win rate drives the loss; MACD cross fires late |
| fractal_dimension_index | Ehlers FDI(30): trade SMA(20) crosses only while FDI < 1.4 (trending) | Big loser: $-8,840.51 combined, 801 trades, PF 0.61 — worst MaxDD in the batch (-32.3% combined); the FDI filter does not keep the system out of losing crosses |

## Empirical direction (batch 28)

Combined batch print: -$46,204.73 across 5,585 trades. No clean winners:
one thin winner (five_zero_pattern +$61.57 on 38 trades), two breakeven
scratches (wilder_volatility_stop -$0.75, shooting_star_pattern +$12.45),
two zero-trade untestables (three_drives_pattern, megaphone_pattern —
both geometric patterns whose full form never completes on 1h crypto),
and seven losers. The batch's lesson is the mirror of batch 27's: the
failure mode is no longer churn alone — it is pattern rarity plus
pullback-entry failure. Geometric/harmonic patterns either never fire
(three drives, megaphone) or fire so rarely their results are noise
(5-0: 38 trades in 7.5 months). The one big loss, ema_pullback
(-$18,418, -$62.0% combined MaxDD), shows the classic pullback trap:
entries trigger on every dip into chop and the EMA(20) exit comes too
late. The FDI experiment (-$8,841) shows a regime filter that cannot
tell a real trend from a noisy SMA cross is worse than no filter.
Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via
the API before building; no duplicates. Backtest numbers were re-run
by the coordinator on the final shipped code and corrected where
builders had mixed the summed-curve final with the closed-trade sum
(rounding_bottom, belt_hold_pattern) or shipped a geometrically
impossible exit (five_zero_pattern: the brief's 38.2% C-to-D exit sat
below the entry and exited 37/38 positions immediately; corrected to
the standard 38.2% retracement of the BC leg from B, as-specified
numbers -$214.27 preserved in its CALIBRATION.md).
## Batch 29 — 2026-11-07

| Strategy | Mechanism | Combined result |
|---|---|---|
| cyber_cycle | Ehlers Cyber Cycle (alpha 0.07), trade Signal crossing its 1-bar delay | Worst in batch: $-11,891 combined, 1,721 trades, PF 0.79 — the Signal cross fires on nearly every wiggle; 33.0% win rate, -46.3% combined MaxDD |
| rsi2_system | Connors RSI(2) ≤5 / ≥95 with SMA(200) filter, exit on close past SMA(5) | Loser: $-4,409 combined, 377 trades, PF 0.56 — 54.1% win rate but avg loss dwarfs avg win; the daily-bars setup does not transfer to 1h crypto |
| dema_cross | DEMA(12) vs DEMA(26) cross | Near breakeven: $-1,318 combined, 967 trades, PF 0.97 — only strategy with a winning coin (HYPE +$2,934, PF 1.19); 686/967 exits are stops |
| macd_zero_line | MACD(12,26,9) line crossing zero | Loser: $-1,592 combined, 594 trades, PF 0.94 — HYPE green (+$918) but BTC/ETH drag it under; 505/594 exits are stops |
| bollinger_breakout | BB(20,2) squeeze (bandwidth lowest 15% of 50 bars) then close outside band | Loser: $-2,822 combined, 567 trades, PF 0.79 — breakouts snap back inside; the close-back-inside exit cuts 87% of trades at a small loss |
| williams_fractals | 5-bar fractal breakout + Alligator (lips>teeth>jaw) filter | Loser: $-5,153 combined, 582 trades, PF 0.80 — red on all three coins; the Alligator filter does not save fractal breaks on 1h |
| one_two_three_reversal | Joe Ross 1-2-3: close beyond point 2, exit below point 3 | Loser: $-2,678 combined, 665 trades, PF 0.91 — HYPE thin green (+$285); 591/665 exits are stops |
| andrews_pitchfork | Pitchfork lower/upper-parallel bounce, target the median line | Loser: $-7,131 combined, 794 trades, PF 0.78 — worst by Sharpe (-3.16); red on all three coins, -25.1% combined MaxDD |
| fibonacci_retracement | Pullback into the 38.2–61.8% golden zone + signal candle, target old high | Loser: $-6,823 combined, 530 trades, PF 0.70 — worst Sharpe in batch (-3.88); ETH/HYPE both worse than -$2,600 |
| floor_pivots | Classic floor pivots from trailing 24 bars: break R1/S1 on volume, target R2/S2 | Only winner: +$1,134 combined, 273 trades, PF 1.09 — HYPE carries it (+$1,667, Sharpe 1.64); BTC red (-$1,091); 201/273 exits are stops |
| morning_star_pattern | Morning/evening star 3-candle reversal with SMA(50) trend filter | Loser: $-697 combined, 148 trades, PF 0.91 — fewest trades in batch; only 11/148 exits on the opposite star, the pattern rarely follows through at 1h |
| chaikin_oscillator | Chaikin Oscillator EMA(3)−EMA(10) of ADL, zero cross + SMA(50) filter | Heavy loser: $-9,414 combined, 1,003 trades, PF 0.70 — red on all three coins; raw zero crosses whipsaw on 1h noise |

## Empirical direction (batch 29)

Combined batch print: -$52,794 across 8,221 trades. One winner
(floor_pivots +$1,134, HYPE-carried and lopsided), one near-breakeven
(dema_cross -$1,318, PF 0.97), ten losers. The batch's lesson is that
the failure mode has converged: whatever the entry trigger — cycle
cross, oscillator zero cross, fractal break, Fib zone, pitchfork
bounce — 1h crypto hands back the same profile, ~30–35% win rate with
losers outweighing winners and 60–90% of exits landing on the 2xATR
stop. The two exceptions are instructive in opposite directions:
floor_pivots wins with the FEWEST trades of any breakout system (273)
and the tightest MaxDD (-6.4%), while cyber_cycle loses the most with
the MOST trades (1,721) — churn, not selectivity, is what kills these
systems. RSI(2) is the cleanest falsification of a famous rule: 54.1%
win rate, PF 0.56 — the bounce is real and still loses money because
the losers are 2–3x the winners. Per-coin detail lives in each
strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via
the API before building; no duplicates. Backtest numbers were re-run
by the coordinator on the final shipped code on the fixed window
(t in [1773525600000, 1794060000000), last completed bar 13:00 UTC
2026-11-07; BTC/ETH 5,704 bars, HYPE 5,702) and corrected where the
builders' standard-runner numbers included the partial 14:00 UTC bar
(dema_cross HYPE 315→314 trades, bollinger_breakout HYPE 211→210
trades, plus 0.01 Sharpe rounding on four rows). No spec corrections
were needed — all twelve briefs were geometrically implementable as
written. No parameters were tuned to PnL.

## Batch 30 — 2026-11-08

| Strategy | Mechanism | Combined result |
|---|---|---|
| narrow_range_breakout | Toby Crabel NR7: narrowest range of 7 bars, breakout of the setup bar's high/low within 24 bars, SMA50>SMA200 filter | Worst in batch: $-18,467 combined, 1,367 trades, PF 0.56 — setups recur every few bars so levels stay armed almost constantly; 23.3% win rate, -61.9% combined MaxDD, worst Sharpe in batch (-7.14) |
| volume_profile_poc | Rolling 168-bar volume profile POC (24 bins, 70% value area); pullback to POC from above, target VAH | Heavy loser: $-14,063 combined, 982 trades, PF 0.53 — the dip condition (low within 0.5xATR of POC) is nearly always true near POC, so it fires on almost every close back across it; Sharpe -9.20, worst in batch |
| sma_rsi_pullback | Pullback to SMA(50) in a SMA50>SMA200 trend with RSI(14) 40–55, entry on close back above SMA(50) | Near breakeven: $-879 combined, 329 trades, PF 0.94 — closest to breakeven in batch; ETH marginally green (+$102, PF 1.02), HYPE red (-$843); 216/329 exits are stops |
| outside_bar_reversal | Outside bar (h>prev h, l<prev l) closing in the outer third, prior trend + volume above average | Loser: $-1,656 combined, 286 trades, PF 0.86 — HYPE green (+$872, PF 1.21) but BTC/ETH drag it under; 33.9% win rate |
| three_white_soldiers | Three consecutive long-bodied bullish candles (open inside prev body, wick ≤25%, body ≥0.5xATR) after a downtrend | Untestable: 0 trades on all three coins — the four-way conjunction three bars running never occurs in 5,223 bars; 169 qualifying bullish candles exist but zero runs of three |
| dark_cloud_cover | Dark cloud cover (bar 2 opens above bar 1 high, closes below midpoint) + piercing-pattern mirror | Untestable: 1 trade total (HYPE long, +$416) — the gap condition is the binding constraint: bar 2 opening above bar 1's high happened twice in 5,223 BTC bars; 24/7 crypto has no session gaps |
| tweezer_reversal | Tweezer top/bottom: two bars with near-equal highs/lows (within 0.1xATR), second bar reversing | Loser: $-998 combined, 442 trades, PF 0.94 — ETH (+$555) and HYPE (+$238) both green, BTC (-$1,791) drags it under; 30.1% win rate |
| rising_three_methods | Rising/falling three methods: long bar-1 candle, three small inside candles, breakout close past bar-1 extreme | Untestable: 1 trade total (ETH long, +$40) — exactly 1 entry signal in ~15,600 bars; the 5-bar structure essentially never completes on 1h crypto |
| stochastics_fast | Fast %K(14)/%D(3) cross from the 80/20 zones with SMA(200) trend filter | Loser: $-2,055 combined, 273 trades, PF 0.69 — red on all three coins; 238/273 exits are signal exits, the crosses reverse too fast to develop |
| adx_di_cross | Wilder +DI/−DI cross with ADX>25 and rising and DI spread ≥5 | Nominal winner: +$476 combined, 8 trades, PF 2.41 — meaningless at n=8; the filter is extremely restrictive on 1h crypto and all profit is 3 HYPE wins |
| ema_ribbon | EMA 8/13/21/34/55 full alignment on first-alignment bar with spread >0.2% | Loser: $-1,778 combined, 452 trades, PF 0.91 — HYPE green (+$1,245, PF 1.19) but BTC/ETH red; entering on the first-alignment bar buys after the move has run; 320/452 exits are stops |
| bollinger_rsi_combo | Bollinger (20,2) band touch + RSI(2) extreme (<10/>90), entry on recovery close back inside the band | Loser: $-6,130 combined, 581 trades, PF 0.71 — 54.6% win rate everywhere yet red on all three coins; average losers dwarf winners, the 2xATR stop takes full losses while the mid-band exit caps winners |

## Empirical direction (batch 30)

Combined batch print: -$45,095 across 4,722 trades. No genuine winner: the three nominally green rows are adx_di_cross (+$476, 8 trades), dark_cloud_cover (+$416, 1 trade) and rising_three_methods (+$40, 1 trade) — all too thin to be edges. Three strategies are effectively untestable as specified on 1h crypto: three_white_soldiers (0 trades), dark_cloud_cover and rising_three_methods (1 trade each). The pattern is the same one batch 28's geometric patterns showed — multi-bar candle structures with strict conjunctions (three-in-a-row, gap opens, five-bar sequences) essentially never complete on 1h crypto bars, and the gap-based dark cloud cover fails outright because 24/7 crypto has no session gaps. The two heaviest losers share a different failure: narrow_range_breakout (-$18,467) and volume_profile_poc (-$14,063) both fire on conditions that are nearly always true (NR7 setups recur every few bars; any pullback sits within 0.5xATR of POC), so they trade the chop at full frequency with 23–28% win rates and -47% to -62% MaxDD. Bollinger+RSI(2) is the cleanest falsification of a famous combo: 54.6% win rate, PF 0.71 — the bounce is real and still loses money because losers run far past winners. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1792328400000), 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC; BTC/ETH 5,223 bars, HYPE 5,221) and matched every builder's numbers exactly — no corrections needed. No parameters were tuned to PnL.

## Batch 31 — 2026-11-09

| Strategy | Mechanism | Combined result |
|---|---|---|
| gann_square_nine | Gann Square of Nine: sqrt-price 45° ladder, cross above/below nearest level within 0.5% of prior close | Worst in batch: $-16,193 combined, 3,027 trades, PF 0.60 — ladder spacing ~0.18% on BTC so it churns ~every 3rd bar; a 0.18% target vs 0.11% round-trip fees leaves nothing; -95.1% BTC MaxDD |
| linear_regression_slope | LinReg(20) OLS slope, entry on slope sign flip with R² ≥ 0.5 | Untestable: 0 trades on all three coins — R² ≥ 0.5 demanded on the exact bar the 20-bar slope flips, but a window straddling a reversal has a poor fit by construction (max R² at any BTC turn 0.265); the briefed rule can essentially never fire |
| time_segmented_volume | Worden TSV(18) = Σ (close − close[1]) × volume, cross of zero | Loser: $-5,396 combined, 1,469 trades, PF 0.88 — HYPE nominally green (+$144, PF 1.01) but BTC (-$5,011) drags it under; 30.9% win rate |
| market_profile_tpo | TPO value area (price-time, 168-bar, 24 bins, 70% VA); breakout above VAH / below VAL | Only nominal winner: +$1,789 combined, 368 trades, PF 1.10 — thin (Sharpe 0.71), carried by HYPE/ETH while BTC lost money; all 368 exits hit the ATR stop/trail, so the opposite-VA-break exit never fired |
| chikou_span_cross | Ichimoku Chikou: close crossing close 26 bars ago | Loser: $-10,842 combined, 1,542 trades, PF 0.74 — 26-period momentum cross whipsaws relentlessly on 1h crypto; 28.7% win rate, -39.5% MaxDD |
| jurik_ma_trend | Jurik MA(14, phase 50) public recursive approximation; cross + rising | Loser: $-13,555 combined, 1,815 trades, PF 0.64 — JMA price cross is a whipsaw machine; low-lag smoothing doesn't help; worst Sharpe in batch (-5.50) after gann |
| mesa_adaptive_ma | Ehlers MAMA/FAMA (Hilbert quadrature, instantaneous period) cross | Loser: $-793 combined, 701 trades, PF 0.97 — closest to breakeven in batch; 561/701 exits are stops |
| smma_cross | Wilder SMMA(9) vs SMMA(21) cross | Breakeven: +$144 combined, 422 trades, PF 1.01 — expectancy $0.34/trade, no edge; ETH -$1,759 vs BTC/HYPE gains is inconsistent |
| wma_cross | WMA(9) vs WMA(21) cross | Loser: $-1,877 combined, 1,131 trades, PF 0.96 — 1,131 whipsaw trades, fees $9,346 |
| td_rei | DeMark REI, 5-bar sum with A/B overlap gate; cross above -60 / below +60 | Heavy loser: $-14,474 combined, 1,706 trades, PF 0.71 — REI whipsaws across ±60 ~7×/day across coins on 1h bars; the daily-bar oscillator fires far too often hourly |
| tenkan_kijun_cross | Ichimoku Tenkan(9) crossing Kijun(26) | Loser: $-3,105 combined, 863 trades, PF 0.91 — mild loser everywhere; 74% of exits are stops; HYPE near breakeven (-$229) |
| kumo_twist | Senkou A crossing Senkou B, spans unshifted (causal) | Loser: $-1,381 combined, 480 trades, PF 0.94 — mildest loser of the batch; HYPE nominally green (+$174); 86% of exits are stops |

## Empirical direction (batch 31)

Combined batch print: -$65,682 across 13,524 trades — the worst batch by dollars so far, and the highest trade count. No genuine winner: the two nominally green rows are market_profile_tpo (+$1,789, PF 1.10, thin) and smma_cross (+$144, PF 1.01, breakeven). One strategy is untestable as specified: linear_regression_slope (0 trades — the R² ≥ 0.5 gate on the exact slope-flip bar can essentially never fire). Two spec corrections surfaced: td_rei ships the canonical 5-bar REI summation (the brief's "8-bar window" is the data lookback, not the sum window); gann_square_nine read "level within 0.5% of price" as within 0.5% of the prior close, which makes trade frequency mostly a function of coin price. The pattern across the batch is the same as ever: fast MA/oscillator crosses on 1h crypto (chikou, jurik, td_rei, gann) churn at 500–3,000 trades with 24–40% win rates and -25% to -55% MaxDD, and the ATR stop/trail does most of the exiting — mesa_adaptive_ma, tenkan_kijun_cross and kumo_twist all exit 74–86% of trades on stops, and market_profile_tpo 100%. The two closest-to-breakeven systems (smma_cross, mesa_adaptive_ma) are the slowest ones in the batch. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794232800000), 2026-03-14 22:00 UTC → 2026-11-09 13:00 UTC; BTC/ETH 5,752 bars, HYPE 5,750) and matched every builder's numbers exactly — no corrections needed. No parameters were tuned to PnL.

## Batch 32 — 2026-11-10

| Strategy | Mechanism | Combined result |
|---|---|---|
| clenow_trend | Clenow trend following: EMA(1200)/EMA(2400) filter, new 1200-bar high/low in trend direction, 3x ATR(720) trail | Loser: $-644 combined, 17 trades, PF 0.33 — slowest system in batch; all 17 trades die on the 3x ATR trail; HYPE 1 win in 11 |
| fisher_acd | Fisher ACD: UTC-day opening range (first 1h bar), A-up/down at ±0.5xATR, C levels at ±1.5xATR, daily-pivot filter | Heavy loser: $-15,495 combined, 1,242 trades, PF 0.66 — single-1h-bar OR is far too narrow; A-points cross on most days, 73.5% of exits are stops; -63.0% BTC MaxDD |
| sperandeo_2b | Sperandeo 2B: new 20-bar high/low, 5–8 bar pullback, breakout bar, close back past the breakout bar's extreme | Loser: $-1,522 combined, 64 trades, PF 0.53 — 63/64 trades die on the ATR stop; the 10x ATR target was never hit on any coin |
| chande_dmi | Chande Dynamic Momentum Index: RSI with volatility-adaptive lookback TD = clamp(14/Vi, 5, 30); 30/70 crosses | Loser: $-7,778 combined, 1,053 trades, PF 0.82 — 30/70 crosses mean-revert into running trends; 64% of exits are stops |
| intraday_momentum_index | Chande IMI(14): RSI on open-to-close moves; 30/70 crosses | Loser: $-5,621 combined, 801 trades, PF 0.84 — 544/801 trades die on the ATR stop; 30/70 crossings mark intraday extremes that keep extending |
| volume_zone_oscillator | Khalil VZO(14): EMA of close-signed volume / EMA of volume; EMA(60) + ADX>18 trend context; -40/+40 and zero crosses | Loser: $-9,567 combined, 919 trades, PF 0.63 — 21.9% win rate, worst in batch; 634/919 exits are signal exits — the VZO cross back through 0 fires almost as soon as the entry cross does |
| bw_market_facilitation_index | Bill Williams BW MFI = (h−l)/v; squat-bar (MFI down, volume up) range breakout within 5 bars + EMA(20) filter | Worst in batch: $-19,687 combined, 3,016 trades, PF 0.65 — squats are ~1/3 of all 1h bars so it fires ~1,000 signals per coin; $13,842 in fees; loses before fees too (-$5,845 gross) |
| polarized_fractal_efficiency | Hannula PFE(10, EMA 5): straight-line vs path efficiency, signed; zero cross after a ±30 extreme | Loser: $-6,265 combined, 1,213 trades, PF 0.84 — 723/1,213 exits are signal exits, so the entries themselves are usually wrong; 30.3% win rate |
| initial_balance_breakout | Steidlmayer Initial Balance: first UTC hour's high/low; closed-bar break, 1x IB extension target, one trade/day | Loser: $-5,606 combined, 712 trades, PF 0.64 — ~1 trade/day; 655/712 exits are signal exits, first-hour breakouts get reclaimed inside the day far more often than they extend |
| connors_double_sevens | Connors Double 7s: daily 7-day-low close above SMA(200), exit on 7-day-high close; long-only, no stop in the original | Loser: $-232 combined, 10 trades, PF 0.46 — the 4800-bar warmup leaves ~40 eligible days; buying 7-day lows in the Oct–Nov downtrend caught falling knives; 4/10 exits were stops (see note) |
| pocket_pivot | Morales/Kacher pocket pivot: up bar whose volume beats every down-day volume of the prior 10 days, EMA(240)>EMA(1200), not extended | Nominal winner, inconclusive: +$263 combined, 5 trades, PF 1.95 — BTC 0 trades (its only signal fired before the 1250-bar warmup); all 5 trades exited on the ATR stop; volume test is the binding constraint (42–58 qualifying bars per coin) |
| weis_wave | David Weis wave: 1.5xATR swing reversal, cumulative volume per wave; new-wave entry when the completed wave's volume < 85% of the prior wave | Loser: $-9,072 combined, 927 trades, PF 0.73 — the 1.5xATR swing flips waves constantly on 1h crypto and the volume filter isn't selective enough |

## Empirical direction (batch 32)

Combined batch print: -$81,225 across 9,979 trades — the worst batch by dollars so far (batch 31: -$65,682) and the second-highest trade count. No genuine winner: the only nominally green row is pocket_pivot (+$263, 5 trades — inconclusive, not an edge). The batch is a tour of published-system ports failing on 1h crypto for three distinct reasons: (1) frequency — bw_market_facilitation_index (3,016 trades) and fisher_acd (1,242) fire on conditions that recur constantly on hourly bars, and the fee bill ($13,842 / $6,887) alone buries them; (2) timeframe mismatch — clenow_trend (17 trades) and connors_double_sevens (10 trades) are daily-scale systems starved by the 8-month window, and initial_balance_breakout's first-hour range is one 1h bar wide; (3) oscillator mean-reversion — chande_dmi, intraday_momentum_index, volume_zone_oscillator and polarized_fractal_efficiency all lose with 22–42% win rates, the 30/70 and zero crosses firing into trends that keep running. The two spec corrections surfaced: clenow_trend's briefed entry (close == the rolling 1200-bar high of `h` including the current bar) is degenerate — close ≤ high on every bar, so it fired 0 times in 17,323 bars; shipped version uses the standard Donchian definition (close above the PRIOR 1200 bars' high). connors_double_sevens' 10x ATR stop was expected to be inert but fired on 4/10 exits — the stop is 10x the *hourly* ATR while positions are held for days, and multi-day drift in the downtrend exceeded it. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794315600000), 2026-03-14 22:00 UTC → 2026-11-10 13:00 UTC; BTC/ETH 5,775 bars, HYPE 5,773) and matched every builder's numbers exactly — no corrections needed. The first coordinator re-run pass used positional index alignment for the combined equity curve and produced slightly different combined Sharpes; the timestamp-aligned re-run (the batch-31 convention: reindex each coin's curve to the union of timestamps, forward-fill, leading gaps at $10k) reproduced every builder's combined Sharpe and MaxDD exactly.

## Batch 33 — 2026-11-11

| Strategy | Mechanism | Combined result |
|---|---|---|
| rwi | Chande & Kroll Random Walk Index: RWI-high/low(14) vs the 1.0 threshold | Loser: $-6,388 combined, 1,641 trades, PF 0.88 — the 1.0 level fires ~500×/coin on 1h bars; BTC -$5,848 (MaxDD -60.7%), HYPE the only green coin (+$1,475) |
| voss_predictive_filter | Ehlers Voss Predictive Filter (period 20, predict 3) crossing the 2-pole band-pass, ADX(14)<25 gate | Loser: $-6,523 combined, 1,322 trades, PF 0.84 — red on all three coins; the 20-bar cycle doesn't persist on hourly bars and the ADX gate doesn't save it |
| ehlers_early_onset_trend | Ehlers Early Onset Trend / Quotient Transform (K1=0.85, K2=0.40 zero crossings) | Near breakeven: $-502 combined, 399 trades, PF 0.97 — closest to breakeven in batch; HYPE +$2,119 (Sharpe 1.56) vs BTC/ETH red; 352/399 exits are ATR stops, the quotient exit almost never acts |
| ehlers_rsi | Ehlers RSI: Wilder RSI(14) on SuperSmoother(10)-filtered closes, 30/70 crosses | Loser: $-2,783 combined, 613 trades, PF 0.90 — best win rate in batch (42.1%) and still red; smoothed mean-reversion catches falling knives |
| connors_cumulative_rsi | Connors Cumulative RSI: cumsum of RSI(2)-50, long above -100 / short below +100, exit at 0 | Nominal winner, thin: +$539 combined, 89 trades, PF 1.21 — 61.8% win rate but ETH -$398 (PF 0.72); 89 trades is not an edge claim |
| supertrend_ema_filter | Supertrend(10, 3.0) with an EMA(200) regime filter | Nominal winner, HYPE-carried: +$1,205 combined, 246 trades, PF 1.10 — BTC/ETH -$769/-$773, HYPE +$2,748; 243/246 exits are stops, the signal exit is nearly dead |
| macd_vwap_combo | MACD(12,26,9) cross with a UTC-day VWAP regime filter | Loser: $-3,655 combined, 1,054 trades, PF 0.91 — ~350 trades/coin, BTC MaxDD -45.2%; fees $7,676 alone exceed the loss; HYPE +$2,830 is the lone green coin |
| bollinger_w_bottom | Bollinger W-bottom / M-top: %B-divergent second low, entry on close back above the middle band | Loser: $-743 combined, 419 trades, PF 0.95 — BTC -$2,387 (PF 0.61); the pattern fires ~1/41 bars, far too permissive vs Bollinger's discretionary W |
| tema_cross | TEMA(9)/TEMA(21) cross, no regime filter | Worst in batch: $-10,514 combined, 1,731 trades, PF 0.82 — unfiltered 9/21 cross whipsaws ~2–3x/day/coin; fees $11,261; BTC -$6,150 (Sharpe -4.47, MaxDD -63.7%) |
| vortex_squeeze | Vortex VI+/VI- cross gated by a Bollinger BandWidth squeeze (lowest 20% of 120 bars) | Loser: $-1,292 combined, 822 trades, PF 0.95 — the squeeze gate cuts trades but doesn't filter losers; roughly breakeven gross, loses to $7,739 in fees; ETH +$1,705 vs BTC -$3,087 |
| donchian_adx | Donchian 20 breakout with an ADX(14)>25 filter, exit on ADX<20 or the opposite breakout | Loser: $-1,653 combined, 340 trades, PF 0.90 — 311/340 exits on the stop, only 29 on signal; ADX>25 selects late entries and breakouts reverse into the stop |
| wilder_volatility_system | Wilder Volatility System: close beyond the prior high/low ± ATR(7) | Only genuine winner: +$3,758 combined, 490 trades, PF 1.16 — HYPE +$2,804 (Sharpe 1.92), ETH +$1,921, BTC -$967; Sharpe 1.20, MaxDD -8.0%; only 9/490 trades ended on the reverse trigger, the rest on the stop/trail |

## Empirical direction (batch 33)

Combined batch print: -$28,551 across 9,166 trades — the smallest dollar loss of any recent batch (batch 32: -$81,225) because trade count fell by ~800 and two systems printed green, but the pattern is unchanged: three nominally green rows, only one with a real sample. wilder_volatility_system (+$3,758, 490 trades, Sharpe 1.20) is the batch's only genuine winner — the Volatility System's ATR(7) breakout filter is the one entry rule in the batch that isn't a cross firing into chop — though even it is carried by HYPE (+$2,804) and ETH (+$1,921) with BTC red, and only 9/490 trades ever reached the reverse trigger, so the shipped result is entry + stop/trail, not the system's own exit logic. supertrend_ema_filter (+$1,205, 246 trades) and connors_cumulative_rsi (+$539, 89 trades) are both HYPE-carried / thin and not edge claims. The two heaviest losers are both fast crosses that fire constantly: tema_cross (1,731 trades, $11,261 in fees) and voss_predictive_filter (1,322 trades) — TEMA's near-zero lag makes 9/21 hug and flip on noise, and the 20-bar Voss cycle doesn't persist on hourly bars. The filtered variants (donchian_adx, vortex_squeeze, supertrend_ema_filter) all show the same lesson as ever: the filter trims frequency without fixing the entry — donchian_adx still exits 311/340 trades on the stop, and vortex_squeeze is breakeven gross before fees. HYPE is positive in 6 of 12 strategies while BTC/ETH lose in the same systems — the window's HYPE trend regime flatters any long-biased or breakout system, so single-coin green prints are artefacts, not cross-coin edge. Spec corrections surfaced: ehlers_early_onset_trend is Ehlers' August 2014 "Quotient Transform" (not a 2016 trigger-line system — two quotients K1=0.85/K2=0.40 traded on zero crossings); connors_cumulative_rsi as briefed (unbounded cumsum, ±100 entries, exit at 0) differs from the published Connors/Alvarez system (bounded 2-reading sum, long-only above SMA200) — shipped as briefed and documented; wilder_volatility_system's trigger uses the current bar's ATR(7) (causal) rather than the previous bar's; voss_predictive_filter's "band-pass line" is the Filt recursion itself (the Wealth-Lab lagging line is the identical 2-pole form). No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; four first picks (td_sequential, mass_index, qstick, camarilla_pivots) already existed on main and were replaced before any code was written. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794402000000), 2026-03-14 22:00 UTC → 2026-11-11 13:00 UTC; BTC/ETH 5,776 bars, HYPE 5,774) and matched every builder's numbers exactly — no corrections needed.

## Batch 34 — 2026-11-12

| Strategy | Mechanism | Combined result |
|---|---|---|
| keltner_channel_breakout | Keltner EMA(20) ± 2xATR(10) breakout, exit on close back inside the channel | Loser: $-9,671 combined, 762 trades, PF 0.53 — exit-on-close-back-inside is a hair trigger, 598/762 exits on signal; 21.9% win rate |
| stochastic_momentum_index | Blau SMI: ±40 crosses, exit at 0 | Only genuine winner: +$1,687 combined, 275 trades, PF 1.13 — ETH +$1,189 (Sharpe 1.15), HYPE +$1,283, BTC -$785; Sharpe 0.78, MaxDD -6.7% |
| bull_bear_power | Elder Bull/Bear Power one-bar turns vs EMA(13) | Loser: $-22,710 combined, 3,613 trades, PF 0.60 — turns fire on ~every 5th bar; end equity $7,274 on $30k; BTC MaxDD -86.7% |
| swing_failure_pattern | Larry Williams 20-bar failed breakout, close back within 3 bars | Loser: $-11,294 combined, 1,305 trades, PF 0.78 — a rolling 20-bar high on 1h crypto is breached routinely; most "failures" are ordinary hourly noise |
| mama | Ehlers MAMA/FAMA cross (canonical Hilbert period, alpha = 0.5/DeltaPhase) | Near breakeven: $-325 combined, 747 trades, PF 0.99 — ETH +$1,574 and HYPE +$641, BTC -$2,540 is the whole loss; Sharpe 0.08 |
| sinewave | Ehlers SineWave/LeadSine cross (FIR Hilbert transformer, instantaneous phase) | Worst in batch: $-28,512 combined, 9,298 trades, PF 0.57 — Hilbert phase whipsaws on 1h noise, ~1 trade every 2 bars; end equity $1,491 on $30k; MaxDD -95.0% |
| vortex_adx | Vortex VI+/VI- cross with ADX(14)>25 filter | Loser: $-9,995 combined, 884 trades, PF 0.61 — ADX filter doesn't save it; 596/884 exits on signal |
| ergodic_indicator | Blau ergodic / TSI (25/13/7) signal-line cross | Loser: $-7,508 combined, 1,467 trades, PF 0.86 — HYPE +$502 the only green coin; closest to breakeven of the cross systems |
| adx_rsi_combo | ADX(14)>25 filter + RSI(14) 30/70 crosses, exit at 50 | Loser: $-1,867 combined, 308 trades, PF 0.87 — best win rate in batch (42.9%) and still red; ETH +$438 vs HYPE -$1,890 |
| donchian_rsi | Donchian 20 breakout + RSI(14) 55/45 confirmation | Loser: $-3,059 combined, 641 trades, PF 0.90 — 626/641 exits on the stop; the RSI confirmation doesn't filter the losers |
| regression_channel | 100-bar OLS channel ±2σ, mean-reversion at bands, exit at midline | Loser: $-6,277 combined, 482 trades, PF 0.71 — red on all three coins; the band touch itself is the losing entry |
| price_channel_breakout | Donchian 30 breakout, exit on close back across the midline | Loser: $-3,292 combined, 515 trades, PF 0.86 — 481/515 exits on the stop; the midline exit almost never fires |
| macd_histogram | Appel MACD(12,26,9) histogram zero cross | Loser: $-4,343 combined, 1,282 trades, PF 0.91 — HYPE +$1,955 vs BTC -$4,313 (MaxDD -49.5%); 780/1,282 exits on the stop |
| ehlers_instantaneous_trendline | Ehlers Instantaneous Trendline (alpha 0.07) cross | Loser: $-19,660 combined, 2,687 trades, PF 0.66 — near-zero-lag line churns on its own signal, 1,837/2,687 exits on signal; MaxDD -66.8% |

## Empirical direction (batch 34)

Combined batch print: -$126,826 across 24,266 trades — the worst batch by dollars so far (batch 32: -$81,225) and the highest trade count, driven by two churn machines: sinewave (9,298 trades, -$28,512, MaxDD -95.0%) and bull_bear_power (3,613 trades, -$22,710, end equity $7,274 on $30k). Only one winner: stochastic_momentum_index (+$1,687, 275 trades, PF 1.13, Sharpe 0.78) — the batch's only genuine winner, though ETH/HYPE-carried with BTC red, so a modest edge claim at best; mama is near breakeven (-$325, PF 0.99). The batch loses even before fees: $110,320 in fees against a -$16,505 gross. BTC is red in all 14 strategies — every system lost on BTC — while HYPE is green in only 4 of 14 and ETH in 4 of 14, so there is no coin-regime excuse this time; the entries themselves fail. Three distinct failure modes, same as ever: (1) frequency — sinewave, bull_bear_power and ehlers_instantaneous_trendline fire on conditions that recur constantly on hourly bars (1 trade every 2–7 bars per coin) and the fee bill alone buries them ($21,546 / $15,667 / $12,789); (2) hair-trigger exits — keltner_channel_breakout's exit-on-close-back-inside (598/762 exits on signal) and price_channel_breakout's midline exit (34/515) mean the systems never hold a winner long enough to pay for the losers; (3) filters that trim without fixing — vortex_adx, adx_rsi_combo and donchian_rsi all show the same lesson: the ADX/RSI filter cuts frequency but the entry still loses (donchian_rsi exits 626/641 trades on the stop). The one system that works, stochastic_momentum_index, is the one whose ±40 trigger levels are far enough apart to let a move develop before the exit fires — 251/275 exits on the stop/trail, only 24 on the zero-line cross. Spec corrections surfaced: mama's briefed alpha formulas matched no published MAMA — shipped the canonical Ehlers/TA-Lib alpha = FastLimit/DeltaPhase; ergodic_indicator's 25/13/7 lengths are identical to the existing true_strength_index (differs only in signal rule and risk layer); vortex_adx used the spec's EMA(14) ratios though the published formula uses 14-period sums; ehlers_instantaneous_trendline needed a 1e-9-relative cross tolerance to suppress float-noise crosses on flat data; sinewave is a real FIR Hilbert + instantaneous-phase build, distinct from the existing ehlers_sinewave (Even Better Sinewave approximation). No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 14 shipped slugs were diffed against main's live tree via the API before building; eight first picks already existed on main (schaff_trend_cycle, guppy_mma, hull_ma_cross, mcginley_dynamic, laguerre_rsi, obv_trend, frama, key_reversal) and were replaced — the local worktree lags main, so local ls checks are NOT authoritative and must never be used as the dedup check again. The duplicate obv_trend and frama builds were deleted before committing; key_reversal was dropped mid-build and replaced with price_channel_breakout. Two build bugs were caught before numbers were recorded (donchian_rsi's runner was briefly a copy of the adx runner; regression_channel's bands lagged an extra 100 bars from a rolling-std construction) — both fixed and re-run. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794488400000), 2026-03-14 22:00 UTC → 2026-11-12 13:00 UTC; BTC/ETH 5,823 bars, HYPE 5,821) and matched every builder's numbers exactly — no corrections needed.

## Batch 35 — 2026-11-13

| Strategy | Mechanism | Combined result |
|---|---|---|
| macd_cross | Appel MACD(12,26,9) signal-line cross, exit on the opposite cross | Loser: $-3,940 combined, 1,280 trades, PF 0.92 — classic cross whipsaw, ~430 trades/coin, $9,099 in fees; HYPE +$2,038 the only green coin |
| atr_trailing_stop | LeBeau Chandelier-style ATR(14) 3x trailing stop, regime flip entries | Winner: +$2,383 combined, 706 trades, PF 1.07 — ETH +$1,723 and HYPE +$1,304, BTC -$644; 664/706 exits on the harness stop, so the regime flip is decorative as an exit |
| hidden_divergence | Wilder RSI(14) hidden divergence on 5-bar pivots, exit at RSI 50 | Loser: $-5,927 combined, 497 trades, PF 0.69 — red on all three coins, 26.8% win rate; the RSI-50 exit genuinely fires (217/497), so it loses on its own terms |
| dual_momentum | Antonacci dual momentum: 240-bar absolute + relative momentum across BTC/ETH/HYPE | Nominal winner, thin: +$731 combined, 371 trades, PF 1.07 — HYPE +$1,254 carries it, ETH -$640; PF within noise of breakeven |
| pairs_spread | Gatev et al. pairs: BTC-ETH log spread, rolling 500-bar beta, z ±2 entries, exit at 0 (single $10k spread book) | Loser: $-1,149 combined, 38 trades, PF 0.49 — only 2/38 exits on the z-cross-0 signal; dislocations kept running against the position |
| markov_regime | Hamilton 2-state Gaussian HMM on 1h log returns (fit on first 1000 bars, causal forward filter); EMA cross in calm state, RSI mean reversion in turbulent state | Loser: $-5,636 combined, 465 trades, PF 0.69 — HMM classifies cleanly (vol-separated states) but the attached EMA/RSI systems have no edge |
| garch_volatility | Bollerslev GARCH(1,1) forecast-vol regime filter on 20-bar breakouts (trade only in the 30th–70th vol band) | Loser: $-1,601 combined, 363 trades, PF 0.82 — 326/363 exits on the range-re-entry signal; normal-vol breakouts don't follow through, worst on HYPE |
| grid_trading | Classic 10-level grid on the trailing 200-bar range; long the bottom 20%, short the top 20%, exit at the midpoint (single-position approximation) | Worst in batch: $-21,422 combined, 963 trades, PF 0.45 — MaxDD -71.5%, end equity $8,657 on $30k; 888/963 trades end on the stop, price almost never returns to the midpoint |
| climax_reversal | Wyckoff buying/selling climax: new 20-bar extreme + volume > 2x mean + close in the far third of the range | Only genuine winner: +$2,583 combined, 264 trades, PF 1.20 — ETH +$3,998 (Sharpe 2.73, PF 1.84) carries it, BTC breakeven, HYPE -$1,246; Sharpe 1.21, MaxDD -8.1% |
| volume_spread_analysis | Tom Williams VSA: no-supply / no-demand bars, stopping volume, upthrusts | Loser: $-8,852 combined, 1,124 trades, PF 0.77 — worst by dollars and drawdown (MaxDD -34.4%); the NS/ND bars fire constantly in ranging 1h crypto |
| breaker_block | ICT SMC breaker block: failed order block flips, short/long on the retest | Loser: $-1,501 combined, 189 trades, PF 0.84 — 174/189 exits on the stop; ETH +$82 is noise-level |
| ict_power_of_three | ICT Power of Three / AMD on UTC days: 8h accumulation range, sweep, reclaim + distribution | Loser: $-3,718 combined, 299 trades, PF 0.63 — 205/299 exits on the day-end signal, so the template was genuinely traded; the UTC-hour-block adaptation is the prime suspect |
| smash_day | Larry Williams Smash Day: wide day (range > 1.5x 20-day mean) then inside day, trade the break of the inside range | Loser: $-953 combined, 39 trades, PF 0.49 — only 39 setups in eight months and all 39 die on the stop; BTC PF 0.14 |

## Empirical direction (batch 35)

Combined batch print: -$49,000 across 6,598 trades — the second-worst batch by dollars (batch 34: -$126,826) but on a third of the trade count, so the per-trade loss is worse: -$7.43/trade vs -$5.23 in batch 34. Three nominal winners, two genuine: climax_reversal (+$2,583, 264 trades, PF 1.20, Sharpe 1.21) and atr_trailing_stop (+$2,383, 706 trades, PF 1.07) — both are entry-selectivity stories where the harness stop/trail does the exiting (climax 232/264 exits on stop, ATR-stop 664/706); dual_momentum (+$731, PF 1.07) is HYPE-carried noise. The rest is a catalogue of the same four failure modes: (1) frequency — macd_cross (1,280 trades, $9,099 fees) and volume_spread_analysis (1,124 trades, $8,912 fees) fire on conditions that recur constantly on hourly bars; (2) trending-window mean reversion — grid_trading (-$21,422, MaxDD -71.5%) and pairs_spread (36/38 exits on stop) both buy dips / fade dislocations that keep running; (3) discretionary-pattern ports — breaker_block, ict_power_of_three and smash_day all lose with the pattern genuinely firing, so the failure is the pattern's 1h transfer, not the implementation; (4) regime machinery that classifies well and trades badly — markov_regime's HMM cleanly separates vol states (BTC sigma 0.0025 vs 0.0064) while the attached systems lose on every coin. BTC is red in 11 of 13 strategies (only atr_trailing_stop's BTC loss is small and dual_momentum's BTC is marginally green); HYPE is green in 5 of 13, ETH in 3 of 13. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 13 slugs were diffed against main's live tree via the API before building; no duplicates. The candle cache was refreshed to the window end before building (BTC/ETH 5848 bars, HYPE 5846 in cache). Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794574800000), 2026-03-14 22:00 UTC → 2026-11-13 13:00 UTC; BTC/ETH 5847 bars, HYPE 5845) and matched every builder's numbers exactly — no corrections needed. Full new test suite: 169 tests green; full strategies package suite: 4004 tests green.

## Batch 36 — 2026-11-14

| Strategy | Mechanism | Combined result |
|---|---|---|
| gonogo_trend | GoNoGo Trend (Alex Cole) weight-of-evidence reconstruction: 5-leg composite score + momentum oscillator (exact vendor formula is proprietary — labeled reconstruction) | Loser: -$7,505 combined, 1,010 trades, PF 0.79 — HYPE +$590 the only green coin; BTC MaxDD -51.4% |
| kase_peak_oscillator | Cynthia Kase Peak Oscillator: KSDI over 10 lookbacks, KaseCD zero cross, PeakOut exits | Loser: -$22,474 combined, 4,015 trades, PF 0.63 — KCD crosses zero every ~4 bars; $17,790 in fees; BTC MaxDD -87.4% |
| dynamic_zone_rsi | Zamansky & Stendahl Dynamic Zone RSI: percentile (12/88 over 70 bars) zones | Loser: -$12,515 combined, 972 trades, PF 0.65 — red on all three coins; BTC MaxDD -56.6% |
| gaussian_filter_trend | Ehlers 4-pole Gaussian filter crossover (P=30 fast / P=10 slow — alpha rises with period, direction corrected, see CALIBRATION.md) | Loser: -$16,257 combined, 2,153 trades, PF 0.72 — $12,012 in fees; worst trade count after Kase |
| renko_brick_reversal | Renko bricks (1.0x ATR) 2-brick reversal | Loser: -$4,571 combined, 245 trades, PF 0.65 — entry structurally late, 205/245 exits on the stop |
| fibonacci_cluster | Fibonacci retracement confluence clusters (38.2/50/61.8 of last 3 swings) | Loser: -$9,709 combined, 961 trades, PF 0.71 — clusters on ~88% of bars, barely filters; BTC MaxDD -46.0% |
| heikin_ashi_delta | Heikin Ashi delta sign-flip momentum | Worst in batch: -$24,193 combined, 4,009 trades, PF 0.60 — HA delta flips every ~8 bars; $15,130 in fees; BTC -90.8% equity |
| cvd_trend | Cumulative Volume Delta (close-location proxy) slope + EMA(50) filter | Loser: -$6,688 combined, 825 trades, PF 0.77 — red on all three coins, HYPE least bad |
| adaptive_supertrend | Supertrend with Choppiness-adaptive ATR multiplier (k 2/3/4) | Nominal winner, noise: +$110 combined, 442 trades, PF 1.00 — HYPE +$3,379 carries it, BTC/ETH red; adaptation barely engages |
| kase_devstop | Cynthia Kase DevStop: two-bar-range stddev band, ratcheted trailing stop as exit | Loser: -$1,800 combined, 1,121 trades, PF 0.90 — DevStop drives exits as designed but the 1.0-sigma band is too tight (~5 flips/day) |
| sine_weighted_ma_trend | Lafferty Sine-Weighted MA(20/40) crossover | Nominal winner, noise: +$700 combined, 488 trades, PF 1.03 — ETH/HYPE green, BTC -$1,919; expectancy +$1.43 vs ~$7.80/trade in fees |
| laguerre_filter_trend | Ehlers Laguerre filter (gamma=0.8) price crossover | Loser: -$6,462 combined, 492 trades, PF 0.61 — 17.7% win rate, worst in batch; filter hugs price, whipsawed out |

## Empirical direction (batch 36)

Combined batch print: -$111,363 across 16,733 trades — the second-worst batch by dollars (batch 34: -$126,826) and -$6.66/trade, between batch 34 (-$5.23) and batch 35 (-$7.43). Zero genuine winners: the two nominal greens, sine_weighted_ma_trend (+$700, PF 1.03) and adaptive_supertrend (+$110, PF 1.00), are both expectancy-under-$1.50 noise against $5–8/trade in fees. The batch loses even before fees: $86,880 in fees against a -$24,483 gross. BTC is red in all 12 strategies, ETH in 11 of 12 (only sine_weighted_ma green), HYPE in 8 of 12 — no coin-regime excuse, the entries fail everywhere. The same four failure modes as ever, with a new fifth: (1) frequency — heikin_ashi_delta (4,009 trades, $15,130 fees) and kase_peak_oscillator (4,015 trades, $17,790 fees) trade ~6x/day/coin on conditions that recur constantly on hourly bars; (2) late entries — gonogo's 5-leg agreement, renko's 2-brick confirmation and fibonacci clusters all enter after the move is spent (renko: 205/245 exits on the stop); (3) daily-bar tools transplanted to 1h — Kase's KCD, the DevStop band and Zamansky's dynamic zones all whipsaw at hourly resolution; (4) regime machinery that classifies well and trades badly — adaptive_supertrend's choppiness adaptation barely engages (k=3.0 on 76–82% of bars); (5) filter math that inverts the signal — the Gaussian filter's alpha rises with period, so the brief's P=10-fast/P=30-slow crossover would have bought tops and sold bottoms (the literal direction also loses, -$14,853). Spec corrections surfaced: gaussian_filter_trend's crossover direction corrected on filter math, not PnL; sine_weighted_ma_trend's attribution corrected to Patrick Lafferty (1999 TASC), not Ehlers; kase_peak_oscillator's warmup 260 → 310 (the rolling-250 percentile window needs 299 bars) and PeakOsc ≥ 0 by construction makes the short-side filter vacuous — the literal spec was shipped and documented rather than inventing an exit; gonogo_trend is a labeled reconstruction, the exact vendor formula being proprietary. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1792328400000), 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC; BTC/ETH 5,223 bars, HYPE 5,221) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 181 tests green; full strategies package suite: 4185 tests green.

## Batch 37 — 2026-11-16

| Strategy | Mechanism | Combined result |
|---|---|---|
| mcclellan_oscillator | McClellan breadth oscillator: EMA19−EMA39 of RANA (24-bar up/down counts); thrust from ±50 through zero | Loser: -$3,980 combined, 190 trades, PF 0.68 — red on all three coins; worst per-trade in the batch (-$20.95) |
| arms_index | Arms TRIN: (up/down bars) / (up/down volume), 10-bar window; contrarian washout extremes | Loser: -$11,241 combined, 1,299 trades, PF 0.77 — red on all three coins, BTC MaxDD -46.1% |
| demark_pivots | Tom DeMark conditional pivots (R1/S1 from prior 24-bar day), break-and-hold entries | Loser: -$12,665 combined, 1,420 trades, PF 0.60 — worst Sharpe in batch (BTC -7.31, MaxDD -59.2%) |
| jurik_rsx | Jurik RSX (public reconstruction): RSI on JMA-smoothed deltas, cross 50 | Loser: -$7,171 combined, 1,030 trades, PF 0.86 — least-bad of the breadth/oscillator group, still red everywhere |
| fft_dominant_cycle | Rolling FFT (128 bars, Hann) top-3 dominant frequencies, SMA(50) filter | Loser: -$9,840 combined, 986 trades, PF 0.72 — BTC Sharpe -5.20, MaxDD -56.1% |
| wavelet_trend | db4 DWT level-3 approximation slope (pure-numpy, symmetric extension) | Loser: -$18,401 combined, 1,792 trades, PF 0.52 — BTC -72.1%, Sharpe -8.97, MaxDD -72.4% |
| bayesian_changepoint | Adams & MacKay BOCD, hazard 1/100, trade post-change mean direction | Loser: -$403 combined, 55 trades, PF 0.89 — least-bad in the batch; HYPE +$1,109 on 5 trades is noise |
| volatility_quality_index | Stridsman VQI: WMA14 of 10-bar summed signed true-range efficiency | Worst in batch: -$20,285 combined, 3,742 trades, PF 0.84 — $26,297 in fees; BTC -88.6%, MaxDD -90.3% |
| dow_theory_trend | Dow swing structure (HH/HL, 5-bar pivots) + volume, 33–66% pullback entries | Loser: -$2,009 combined, 262 trades, PF 0.85 — HYPE +$469 the only green coin-leg outside BOCD/elliott |
| elliott_wave_count | Strict 5-wave impulse + ABC count (wave-2 38.2–61.8%, wave-3 never shortest) | Break-even noise: -$44 combined, 34 trades, PF 0.95 — strict rules prune nearly everything; BTC +$58, HYPE +$58 (1 trade) |
| schwager_volatility_ratio | Schwager VR = TR / EMA(TR): fade VR > 2.0 wide bars | Loser: -$8,810 combined, 515 trades, PF 0.62 — -$17.11/trade, second-worst per-trade; wide bars keep running |
| prev_day_high_low | Prior UTC-day high/low breakout + 0.1% filter | Loser: -$7,046 combined, 604 trades, PF 0.75 — 29.6% win rate, red on all three coins |

## Empirical direction (batch 37)

Combined batch print: -$101,897 across 11,929 trades — third-worst batch by dollars (batch 34: -$126,826; batch 36: -$111,363) but the worst per-trade yet at -$8.54/trade (batch 35: -$7.43; batch 36: -$6.66). Zero genuine winners and zero green strategies: the least-bad, elliott_wave_count (-$44, 34 trades) and bayesian_changepoint (-$403, 55 trades), are both break-even noise on tiny samples. The batch loses even before fees: $93,028 in fees against a -$8,869 gross. BTC is red in 11 of 12 (only elliott's +$58 on 20 trades green), ETH red in 12 of 12, HYPE red in 9 of 12 (BOCD's +$1,109 on 5 trades, dow's +$469 and elliott's +$58 on 1 trade are the only greens). The failure modes: (1) frequency — volatility_quality_index (3,742 trades, $26,297 fees) and wavelet_trend (1,792 trades, BTC Sharpe -8.97) trade on conditions that recur constantly on hourly bars; (2) breadth proxies that don't transfer — mcclellan (worst per-trade, -$20.95) and arms_index both lose on every coin, the single-asset candle-count proxy carries no breadth signal; (3) cycle machinery — fft_dominant_cycle and wavelet_trend both assume stationary cycles and lose everywhere (wavelet BTC -72.1%, MaxDD -72.4%); (4) discretionary-pattern ports — demark_pivots (BTC Sharpe -7.31, MaxDD -59.2%) and dow_theory_trend lose with the pattern genuinely firing; (5) fade-the-extreme — schwager_volatility_ratio (-$17.11/trade) fades wide bars that keep running. Spec corrections surfaced: mcclellan/arms "after being beyond" read as a prior-10-bar excursion, not a one-bar jump (a literal jump never occurs on 1h bars); jurik RSX implemented from the exact public-reconstruction formula in the Wickra docs, verified against the source page; wavelet DWT switched from a circular to a symmetric-extension filter bank after the wrap discontinuity contaminated the traded value; BOCD kappa0=5, not 1 — at kappa0=1 the 0.5 threshold never fires, verified numerically; dow pullback range frozen at the leg that formed the last swing extreme (otherwise the pullback's own confirmation resets the range to 100% depth); elliott wave-3-shortest checked at wave-4 confirmation, the only implementable point; schwager entries and the PDH midnight-flat exit execute at the next bar's open per the harness, not at the next close / on the midnight bar. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794924000000), 2026-03-14 22:00 UTC → 2026-11-17 14:00 UTC; BTC/ETH 5,944 bars, HYPE 5,942) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 227 tests green.

## Batch 38 — 2026-11-17

| Strategy | Mechanism | Combined result |
|---|---|---|
| heikin_ashi_macd | Heikin Ashi candles + MACD(12,26,9) on HA close; histogram zero-cross with HA direction (Raisontgh TradingView) | Loser: -$2,501 combined, 1,168 trades, PF 0.95 — HYPE +$2,591 the only green coin; BTC/ETH red, fees $8,758 |
| cci_macd_combo | CCI(14) ±100 crosses confirmed by MACD line vs signal | Loser: -$899 combined, 87 trades, PF 0.75 — most selective in batch; MACD-agreement filter binds, entries land late |
| triple_rsi | RSI(7/14/21) full agreement (all >55 long / all <45 short), exit on any RSI crossing 50 | Worst by dollars: -$11,465 combined, 1,294 trades, PF 0.73 — BTC Sharpe -3.74, MaxDD -40.4%; buys tops, sells bottoms |
| volume_ma_breakout | 20-bar high/low breakout + volume > 1.5x 20-bar mean | Loser: -$5,922 combined, 824 trades, PF 0.84 — fees $6,140 exceed the net loss; 730/824 exits on the stop |
| swing_high_low_breakout | 5-bar pivot HH/HL structure breakout (ascending lows / descending highs) | Loser: -$10,731 combined, 825 trades, PF 0.70 — worst Sharpe in batch (-3.50); ETH -$4,810, PF 0.57 |
| support_resistance_flip | Break-and-retest role reversal: 50-bar pivot levels (≥2 touches), break then retest-hold within 20 bars | Loser: -$8,363 combined, 1,249 trades, PF 0.77 — lowest win rate (23.8%); signal exits outnumber stops — the retest "hold" fails by the next open |
| trendline_breakout | Demark-style trendlines through last two 10-bar pivots, break = cross | Loser: -$8,054 combined, 959 trades, PF 0.79 — 709/959 exits on the stop; trendline breaks chase spent moves |
| supertrend_rsi | Supertrend(10,3) + RSI(14) 50-cross; exit on Supertrend flip | Loser: -$2,431 combined, 488 trades, PF 0.90 — only 36/488 exits on the Supertrend flip; the exit is decorative |
| ichimoku_macd | Ichimoku (9/26/52) cloud + Tenkan/Kijun cross, MACD histogram agreement | Least-bad: -$254 combined, 293 trades, PF 0.98 — HYPE +$936 (PF 1.22) the only winning coin-leg of note; near breakeven, still red |
| adx_ema_trend | EMA(20/50) cross with ADX(14) > 25 and +DI/-DI agreement | Least-bad by dollars: -$573 combined, 76 trades, PF 0.82 — ADX filter too strict for 1h crypto; 69/76 exits on the stop |
| rsi_volume_confirmation | RSI(14) 50-cross + volume > 1.25x 20-bar mean | Loser: -$2,689 combined, 675 trades, PF 0.89 — 26.2% win rate; ETH +$147 is the batch's only green ETH leg |
| donchian_macd | Donchian(20) breakout (previous 20 bars) + MACD histogram agreement | Loser: -$2,837 combined, 711 trades, PF 0.91 — 20-bar breakouts on 1h are mostly false breakouts; MACD does not filter them |

## Empirical direction (batch 38)

Combined batch print: -$56,719 across 8,649 trades (-$6.56/trade), zero genuine winners and zero green strategies — the least-bad, ichimoku_macd (-$254, PF 0.98) and adx_ema_trend (-$573, PF 0.82), are both break-even noise. Unlike batches 36–37 the batch is gross-positive before fees (+$5,598 gross vs $62,318 in fees): the entries roughly break even and the fee schedule does the killing. BTC is red in 12 of 12 strategies, ETH in 11 of 12 (only rsi_volume_confirmation's +$147 green), HYPE in 9 of 12 (heikin_ashi_macd +$2,591, ichimoku_macd +$936, adx_ema_trend +$328 the only greens). The failure modes: (1) frequency — triple_rsi (1,294 trades), heikin_ashi_macd (1,168) and support_resistance_flip (1,249) trade on conditions that recur constantly on hourly bars; (2) late entries — triple_rsi's full-agreement rule, trendline breaks and cci_macd_combo's MACD-agreement filter all enter after the move is spent; (3) confirmation filters that don't filter — volume (1.25x/1.5x), MACD histogram agreement and ADX > 25 all lose with the filter genuinely engaging; (4) retest entries that fail immediately — support_resistance_flip's signal exits outnumber stops, the one-bar hold does not survive to the next open. Spec corrections surfaced: donchian_macd's close-breakout and volume_ma_breakout's exit must use the *previous* N bars — the literal "incl. current bar" reading can never fire (trailing high incl. current is always ≥ close); swing pivots are recorded at the confirmation bar (centre + 2), not the centre bar; trendline breaks are crosses, not levels; ichimoku uses the plotted (displaced) cloud and excludes the Chikou span, which the shared helper computes 26 bars into the future (lookahead). No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1794924000000), 2026-03-14 22:00 UTC → 2026-11-17 14:00 UTC; BTC/ETH 5,944 bars, HYPE 5,942) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 206 tests green.
## Batch 39 — 2026-11-18

| Strategy | Mechanism | Combined result |
|---|---|---|
| stochastic_rsi | StochRSI(14,3,3) %K/%D cross out of <20 / >80 zones (Chande & Kroll) | Worst by dollars: -$17,715 combined, 2,166 trades, PF 0.62 — %K whipsaws across %D several times a day; BTC Sharpe -6.89, MaxDD -69.1% |
| atr_breakout | 20-bar close-range breakout + 0.25xATR buffer, ATR(14) above its 20-bar mean | Loser: -$1,179 combined, 155 trades, PF 0.72 — most selective in batch; breaks mostly fail immediately |
| london_breakout | London session range (00:00–08:00 UTC) breakout, 08:00–12:00 entry window, 16:00 time exit | Loser: -$1,853 combined, 345 trades, PF 0.87 — ETH +$850 the only green coin; no session open exists in 24/7 crypto |
| sfp | Swing Failure Pattern: sweep of a 5-bar pivot + close back inside, volume > 1.5x | Loser: -$8,569 combined, 617 trades, PF 0.64 — the sweep is continuation, not failure; price keeps going through the level |
| choch | Change of Character: close beyond the protected swing + displacement body > 1.5xATR | Least-bad by win rate: -$1,144 combined, 225 trades, PF 0.80 — 42.2% win rate, best in batch; signal exit cuts trades fast but breaks reverse |
| vcp | Volatility Contraction Pattern (Minervini): shrinking pullbacks, pivot breakout on volume | Loser: -$3,058 combined, 180 trades, PF 0.55 — worst expectancy in batch (-$16.99/trade); breakouts close back below the pivot within a few bars |
| two_b | Sperandeo 2B: new 20-bar extreme, pullback, failed retest, close back through the retest bar | Loser: -$1,024 combined, 39 trades, PF 0.51 — most selective failure; 36/39 exits on the stop |
| quasimodo | Quasimodo: HH, break of last HL, failed retest of the left shoulder, close below the shoulder's low | Nominal winner: +$573 combined, 22 trades, PF 1.62 — entire profit is 4 ETH trades (PF 8.29); BTC and HYPE both red; indistinguishable from luck |
| three_bar_triangle | Raschke 3-bar triangle: inside-bar contraction, breakout on 1.25x volume | Loser: -$10,225 combined, 1,134 trades, PF 0.76 — contractions fire constantly on 1h crypto; volume filter does not separate real breakouts |
| supertrend_parabolic | Supertrend(10,3) + PSAR(0.02, 0.2) agreement (price above/below both) | Loser: -$6,231 combined, 937 trades, PF 0.84 — BTC Sharpe -2.06, MaxDD -41.7%; agreement turns on after the move |
| parabolic_adx | PSAR flip gated by ADX(14) > 25 + DI agreement | Loser: -$3,759 combined, 261 trades, PF 0.68 — worst expectancy per trade among trend filters (-$14.40); ADX gate does not save SAR flips |
| bollinger_macd | Lower/upper band tag + MACD cross within 3 bars | Least-bad: -$933 combined, 221 trades, PF 0.88 — 47.1% win rate, best in batch; HYPE +$209 (PF 1.11) the only green HYPE leg; only strategy where signal exits outnumber stops |

## Empirical direction (batch 39)

Combined batch print: -$55,116 across 6,302 trades (-$8.75/trade) — the worst per-trade batch yet (batch 37: -$8.54) and -$55,116 by dollars, slightly better than batch 38's -$56,719. One nominal winner (quasimodo +$573 on 22 trades, all profit from 4 ETH trades) and zero robust winners. The batch loses even before fees: -$14,071 gross vs $41,045 in fees. BTC is red in 12 of 12 strategies, ETH in 10 of 12 (only london_breakout +$850 and quasimodo +$983 green), HYPE in 11 of 12 (only bollinger_macd +$209 green). Failure modes: (1) oscillator whipsaw — stochastic_rsi's %K crosses %D 2,166 times and three_bar_triangle's contractions fire 1,134 times; (2) failed-breakout logic that buys the failure — sfp (-$8,569) and two_b both trade the failed extreme and lose, because on 1h crypto the sweep is usually continuation; (3) structure breaks that reverse — choch's displacement breaks and quasimodo's shoulders both print and then reverse before follow-through; (4) session structure that doesn't exist — london_breakout's 00:00–08:00 UTC range carries no information in a 24/7 market; (5) confirmation filters that don't filter — ADX > 25, volume 1.25–1.5x, and MACD agreement all lose with the filter genuinely engaging. Spec corrections surfaced: PSAR seeded from bar 0 only (seeding from the first two closes would peek at bar 1); london_breakout uses fixed UTC hours (the winter/GMT reading; BST shifts +1h in summer) and close-based entries with the both-sides-break skip judged on wicks; stochastic_rsi's StochRSI falls back to 50.0 when the RSI range collapses to zero on monotonic moves (the oscillator goes blind in trends); two_b's retest check must run before the new-high re-arm check or the retest bar re-arms the pattern; vcp legs update in place when a later low extends the same swing high (otherwise one high + two lows fakes a two-leg chain). No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795010400000), 2026-03-14 22:00 UTC → 2026-11-18 14:00 UTC; BTC/ETH 5,968 bars, HYPE 5,966) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 228 tests green.
## Batch 40 — 2026-11-19

| Strategy | Mechanism | Combined result |
|---|---|---|
| smt_divergence | ICT SMT divergence: BTC makes a new swing low ETH fails to confirm (and mirror), entry on the structure shift | Loser: -$1,452 combined, 288 trades, PF 0.90 — fees $2,916 exceed the loss, gross roughly breakeven; the ETH/BTC book's +$181 is noise |
| judas_swing | ICT Judas swing: Asian-range sweep at the London open, reclaim + structure shift, fade the fakeout | Loser: -$2,153 combined, 105 trades, PF 0.61 — the sweep more often continues than reverses, on all three coins |
| new_york_open | NY open 13:00 UTC first-hour range breakout, 14:00–17:00 entry window, 21:00 time exit | Loser: -$2,854 combined, 628 trades, PF 0.86 — BTC -$2,949 (MaxDD -33.5%) worst; HYPE +$573 is noise; breaks fade into the time exit |
| hurst_exponent_regime | Rolling R/S Hurst (200 bars): H>0.55 trend mode trades EMA crosses, H<0.45 reversion mode fades RSI extremes | Nominal winner: +$587 combined, 256 trades, PF 1.05 — entirely HYPE-carried (+$1,541); mean H ≈ 0.59, so the reversion leg fires on ~1% of bars — effectively trend-only |
| volatility_regime_switch | ATR(14) percentile: >60 Donchian(20) breakout, <40 Bollinger(20,2) fade | Loser: -$6,544 combined, 785 trades, PF 0.80 — fees $5,631 are 86% of the loss; both legs lose |
| turn_of_month | Calendar long: last day of the month through the 3rd day of the next (Lakonishok & Smidt window) | Loser: -$793 combined, 24 trades, PF 0.37 — worst per-trade in batch (-$33.04); every trade dies on the 2xATR stop before the day-3 calendar exit fires once |
| value_area_breakout | Prior-day volume profile (50 bins, 70% value area): two-close acceptance beyond VAH/VAL | Loser: -$6,286 combined, 947 trades, PF 0.80 — fees $6,675 exceed the loss; two-close acceptance fires ~4 trades/day on noise around a single-day level |
| balanced_price_range | ICT BPR: overlap of opposite FVGs within 60 bars, entry on the return into the zone | Nominal winner: +$387 combined, 509 trades, PF 1.02 — entire profit is HYPE (+$3,337); BTC -$3,198 (PF 0.43); fees $4,117 are >10x the profit |
| mitigation_block | ICT mitigation block: failure swing (no new extreme) + structure break, entry on the return to the block | Loser: -$3,516 combined, 411 trades, PF 0.79 — 255/411 exits on the stop; ETH +$210 is flat noise |
| livermore_pivotal | Livermore Market Key: narrow-range consolidation pivot, volume break + low-volume reaction + resumption | Loser: -$502 combined, 116 trades, PF 0.92 — BTC +$367 and ETH +$693 wiped out by HYPE -$1,562; gross roughly breakeven |
| schiff_pitchfork | Schiff pitchfork median-line pullback (anchor at (A+B)/2, not at A) | Worst by dollars: -$13,889 combined, 1,597 trades, PF 0.73 — the Schiff line sits close to price by design, so touches fire constantly; MaxDD -50.2% |
| fibonacci_time_zones | Fib time zones (8/13/21/34 bars after a swing) gating EMA pullback entries | Nominal winner: +$1,349 combined, 128 trades, PF 1.21 — best PF in batch, but HYPE (+$1,358) supplies all of it; BTC loses, ETH flat |

## Empirical direction (batch 40)

Combined batch print: -$35,666 across 5,794 trades (-$6.16/trade). Three nominal winners (fibonacci_time_zones +$1,349, hurst_exponent_regime +$587, balanced_price_range +$387), all thin, all HYPE-carried, zero robust winners. The batch is gross-positive before fees (+$6,068 gross vs $41,733 in fees): the entries roughly break even and the fee schedule does the killing — the same shape as batch 38. BTC is red in 11 of 12 strategies (only livermore_pivotal's +$367 green), ETH green in 6 of 12, HYPE green in 4 of 11 (smt_divergence has no HYPE book). Failure modes: (1) frequency — schiff_pitchfork (1,597 trades), value_area_breakout (947) and volatility_regime_switch (785) trade on conditions that recur constantly on hourly bars; (2) session structure that doesn't exist — judas_swing and new_york_open both lose, the same verdict batch 39's london_breakout gave for London; (3) sweeps continue — judas_swing and mitigation_block both fade the sweep and lose, because on 1h crypto the sweep is usually continuation; (4) calendar effects don't survive the stop — turn_of_month's 2xATR stop kills all 24 trades before the day-3 exit fires once; (5) regime switches that don't switch — Hurst's mean ≈ 0.59 (R/S small-sample bias) keeps hurst_exponent_regime in trend mode 72–75% of bars, so the reversion leg is untested. Spec corrections surfaced: Hurst hysteresis counts only consecutive bars in the *same* new band (a bar in a third band restarts the count); smt_divergence's combined row pools two $10k books ($20k start); value-area consecutive-close streaks reset at each UTC-day boundary; BPR "traded beyond" is a close beyond the zone, not a wick poke; the mitigation block is the L1/H1 centre-bar candle and "never traded through" is enforced on wicks; schiff_pitchfork and fibonacci_time_zones use 10-bar pivots on the window [j−7, j+2] so confirmation at centre+2 stays causal; judas_swing's London window is bars opening 07:00–09:00 with reclaim/shift allowed to the 12:00 deadline; new_york_open's same-day range is NaN before 13:00 (a lookahead leak found in testing). No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795096800000), 2026-03-14 22:00 UTC → 2026-11-19 14:00 UTC; BTC/ETH 5,992 bars, HYPE 5,990) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 199 tests green.
## Batch 41 — 2026-11-20

| Strategy | Mechanism | Combined result |
|---|---|---|
| bollinger_keltner_squeeze | Carter TTM Squeeze: BB(20,2) inside KC(20,1.5xATR), fire + 20-bar momentum-histogram direction | Nominal winner: +$366 combined, 379 trades, PF 1.02 — ETH +$740 the only green coin-leg of substance; Keltner mid is EMA(20), Bollinger mid SMA(20); shipped win does not survive either calibration alternate |
| adaptive_macd | MACD on Kaufman efficiency-ratio adaptive EMAs (fast 2..12, slow 5..26), cross vs 9-bar signal | Loser: -$5,588 combined, 998 trades, PF 0.87 — HYPE +$331 the only green coin; ER=0 on flat stretches, signal EMA seeded from first MACD value |
| heikin_ashi_ema | Heikin Ashi candle direction + EMA(9/21/50) trend filter | Worst by dollars: -$24,287 combined, 2,895 trades, PF 0.51 — BTC MaxDD -90.9%, combined end equity $5,731; entry is a state, not a transition, so it re-enters every qualifying bar (~1 trade per 6 bars per coin) |
| volume_weighted_rsi | RSI(14) on rolling 14-bar volume-weighted typical price; cross out of 30/70, exit at 50 | Loser: -$4,063 combined, 510 trades, PF 0.84 — best win rate in batch (40.0%) still loses; base.rsi fills pre-valid values with 0, WARMUP=40 suppresses the spurious first-value cross |
| vwap_bollinger_bands | UTC-day session VWAP ±2.0 volume-weighted SD bands, ADX(14) < 25 regime filter, exit at VWAP | Loser: -$11,712 combined, 1,078 trades, PF 0.60 — highest win rate in batch (52.3%) and still the second-worst by dollars; wins are small, losses are full stops; 24/7 crypto has no true session open, the UTC-day anchor is the adaptation |
| donchian_ema_filter | Donchian(20) close breakout (prior 20 bars) + EMA(50) trend filter, Turtle 10-bar exit | Loser: -$3,120 combined, 660 trades, PF 0.90 — ETH +$154 is flat noise; the Turtle 10-bar exit almost never fires at 1h horizon (69/660 signal exits) |
| supertrend_macd | Supertrend(10,3) direction + MACD histogram sign agreement | Loser: -$4,574 combined, 896 trades, PF 0.88 — loses on all three coins; Supertrend seeds at the first bar with a valid ATR (bar 9), not bar 0 |
| psar_macd | PSAR(0.02,0.2) flip + MACD line-vs-signal agreement | Loser: -$2,406 combined, 674 trades, PF 0.92 — HYPE +$3,054 (PF 1.25) is the batch's best single coin-leg; BTC/ETH both ~-$2,700; PSAR seeded from bar 0 only |
| ema_vwap_momentum | EMA(9/21) cross + close vs session VWAP, exit on cross-against or close back through VWAP | Loser: -$5,590 combined, 799 trades, PF 0.79 — HYPE +$1,219 the only green coin; the VWAP leash does most of the exiting (489 signal exits vs 310 stops) |
| bollinger_reversion | Bollinger(20,2) band-tag fade, exit at the middle band | Loser: -$17,012 combined, 1,104 trades, PF 0.58 — worst Sharpe in batch (-6.27), MaxDD -57.4%; the tag is continuation, not reversion, on 1h crypto |
| stochastic_macd | Stochastic(14,3,3) %K/%D cross out of 30/70 + MACD histogram agreement | Loser: -$1,258 combined, 97 trades, PF 0.60 — most selective in batch; the cross and the histogram flip miss each other by a bar on most setups, so it rarely fires |
| weekly_pivot_breakout | Prior completed UTC-week high/low breakout (wick levels, close entries), exit on close back inside | Loser: -$16,032 combined, 704 trades, PF 0.43 — worst win rate in batch (18.3%) and worst PF; per-coin losses near-identical (-$5,338/-$5,358/-$5,336); first partial week excluded (levels appear at bar 194) |

## Empirical direction (batch 41)

Combined batch print: -$95,275 across 10,794 trades (-$8.83/trade) — the worst batch by dollars yet (batch 38: -$56,719) and the worst per-trade since batch 39 (-$8.75). One nominal winner (bollinger_keltner_squeeze +$366 on 379 trades, PF 1.02, does not survive calibration) and zero robust winners. BTC is red in 12 of 12 strategies, ETH in 11 of 12 (only donchian_ema_filter's +$154 green), HYPE in 9 of 12 (psar_macd +$3,054, ema_vwap_momentum +$1,219, adaptive_macd +$331 the only greens). Failure modes: (1) state-not-transition entries — heikin_ashi_ema re-enters every qualifying bar and churns 2,895 trades into a -90.9% BTC MaxDD; (2) band-tag fades that buy continuation — bollinger_reversion (-$17,012) and vwap_bollinger_bands (-$11,712) both lose with the highest win rates in the batch (41.9% and 52.3%), the wins are small and the stops are full-size; (3) agreement filters that agree too late — supertrend_macd, psar_macd, stochastic_macd and ema_vwap_momentum all require two indicators to line up and still lose on BTC/ETH; (4) weekly structure that doesn't hold — weekly_pivot_breakout's 18.3% win rate is the lowest of any batch-41 strategy and its PF (0.43) the worst; (5) exits that never fire — donchian_ema_filter's Turtle 10-bar exit fires on 69/660 trades, so the 2xATR stop does the exiting. Spec corrections surfaced: squeeze momentum is first valid at bar 38 (20 bars of x, then a 20-bar regression), not bar 19; Supertrend seeds at the first valid-ATR bar, not bar 0; PSAR seeds LONG from bar 0 only (SAR = low[0], EP = high[0]); weekly levels require a complete 168-bar week; vwap_bollinger_bands' ADX is a global ewm, not session-reset, and is NaN for ~27 bars from window start; volume_weighted_rsi's first genuine RSI value registers as a cross from base.rsi's 0-fill, suppressed by WARMUP=40. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795183200000), 2026-03-14 22:00 UTC → 2026-11-20 14:00 UTC; BTC/ETH 6,016 bars, HYPE 6,014) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 235 tests green.

## Batch 42 — 2026-11-21

| Strategy | Mechanism | Combined result |
|---|---|---|
| donchian_breakout | Donchian(20) prior-bar channel breakout, Turtle 10-bar exit | Loser: -$2,098 combined, 667 trades, PF 0.93 — ETH +$382 the only green coin-leg; 595/667 exits on the harness stop |
| triple_ema_cross | EMA(5/13/50) full alignment + 5/13 cross, exit on cross back | Loser: -$5,244 combined, 539 trades, PF 0.75 — loses on all three coins; alternate 9/21/55 wins +$2,227 on all three (extreme parameter sensitivity, not adopted) |
| obv_breakout | OBV (Granville) vs its prior-20-bar high/low | Loser: -$1,847 combined, 909 trades, PF 0.96 — near breakeven; fees $6,845 exceed the net loss |
| rsi2_connors | Connors RSI(3) <10 long / >90 short, exit at 50 | Loser: -$4,722 combined, 452 trades, PF 0.61 — best win rate in batch (58.0%) and still loses; average losses ~1.5x average wins |
| stoch_rsi_cross | StochRSI(14,14,3,3) %K/%D cross out of 20/80 | Loser: -$14,864 combined, 1,493 trades, PF 0.48 — worst PF in batch; 1,296/1,493 exits are the opposite cross, churns to death on fees |
| macd_histogram_divergence | MACD histogram divergence on confirmed (±2-bar) pivots | Loser: -$2,214 combined, 475 trades, PF 0.90 — thinnest loser; HYPE +$1,012 the only green coin-leg; 318/475 exits on the stop |
| williams_vix_fix | WVF fear-spike flash long / inverted flash short (Larry Williams) | Loser: -$8,284 combined, 1,313 trades, PF 0.83 — gross ≈ -$210 before fees; fees do the killing |
| center_of_gravity | Ehlers CG vs SMA(3) trigger | Loser: -$20,893 combined, 3,657 trades, PF 0.70 — MaxDD -69.9%; assigned weight convention is the reverse of Ehlers' original (documented, not corrected) |
| relative_vigor_index | Ehlers RVI vs 4-bar weighted signal | Worst by dollars: -$25,796 combined, 5,248 trades, PF 0.61 — MaxDD -86.4%, end equity $4,238; negative even before fees (-$8,669 gross) |
| chande_momentum | CMO(14) cross above -50 / below +50 | Loser: -$5,753 combined, 587 trades, PF 0.80 |
| pivot_camarilla | Prior-day Camarilla R3/S3 breakout (factor 1.055 as assigned) | Loser: -$1,523 combined, 250 trades, PF 0.84 — most selective in batch; HYPE +$673 the only green coin-leg |
| accumulation_distribution | Chaikin A/D line vs SMA(20) | Loser: -$16,977 combined, 2,304 trades, PF 0.68 — ~1 trade per 2.6 bars; BTC MaxDD -74.9% |

## Empirical direction (batch 42)

Combined batch print: -$110,216 across 17,894 trades (-$6.16/trade) — the second-worst batch by dollars (batch 34: -$126,826) and the worst by dollars since batch 34; per-trade is better than batch 41 (-$8.83), which remains the worst per-trade. Zero winners of any kind — 12/12 losers, the first all-loser batch (batch 41 had one nominal +$366 winner). Fees total $93,457, 85% of the loss. BTC is red in 12 of 12 strategies, ETH in 12 of 12, HYPE in 10 of 12 (only macd_histogram_divergence +$1,012 and pivot_camarilla +$673 green). Failure modes: (1) oscillator crosses that whipsaw — relative_vigor_index (5,248 trades), center_of_gravity (3,657), stoch_rsi_cross (1,296 of 1,493 exits are the opposite cross); (2) dip-buying in a downtrend window — rsi2_connors posts the batch's best win rate (58.0%) and still loses with PF 0.61, average losses ~1.5x average wins; (3) divergence that doesn't mark turns — macd_histogram_divergence's entries end on the stop 318/475 times; (4) fear-spike fades — williams_vix_fix is gross ≈ breakeven (-$210) and the fees kill it; (5) volume-flow lines that trade constantly — accumulation_distribution fires ~1 trade per 2.6 bars and its BTC leg draws down -74.9%. Spec corrections surfaced: the assigned Camarilla factor 1.055 is ~3.8x the canonical R3 offset (0.275) and ~1.9x R4 (0.55) — implemented as assigned, canonical run as an alternate (loses far more); center_of_gravity's assigned weights (most recent price weight 10) are the reverse of Ehlers' original, so CG moves opposite to price — documented, not corrected; Connors RSI ships RSI(3) of the streak per the brief vs the canonical RSI(2) (canonical alternate loses more); triple_ema_cross's 9/21/55 alternate wins on all three coins while the shipped 5/13/50 loses on all three — extreme parameter sensitivity, not adopted; pivot crosses are judged against the current bar's level so a UTC-day-boundary level jump cannot fire a signal by itself; the Donchian channel excludes the current bar (prior 20 bars only); the Turtle skip rule was not implemented (spec omitted it); MACD divergence is read at the confirmation bar (pivot+2), not the pivot bar. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795269600000), 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC; BTC/ETH 6,040 bars, HYPE 6,038) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin. Full new test suite: 192 tests green.

## Batch 43 — 2026-11-22

| Strategy | Mechanism | Combined result |
|---|---|---|
| btc_breakout_trend_climber | QuantConnect BTC Breakout Trend Climber: close above 25-day high or upper BB(50, 2.1σ), ATR-staged exits | Nominal winner: +$2,322 combined, 140 trades, PF 1.25 — 94% of profit is HYPE (+$2,175, PF 2.13); BTC -$527 (PF 0.86), ETH +$673; win rate 30.0% |
| oliver_kell_ema_reclaim | Oliver Kell 20-EMA reclaim: cross back above 20 EMA after a 5–19% pullback on quiet volume, above rising 200 SMA | Loser: -$154 combined, 59 trades, PF 0.90 — BTC 0 trades (the 5–19% pullback band never binds on 1h); HYPE -$169, ETH +$15 |
| squeeze_momentum | LazyBear Squeeze Momentum: BB(20,2) inside KC(20,1.5xATR) release + rising positive linreg momentum at its 100-bar low, close above EMA(100) | No trades: 0 combined, 0 trades — the 100-bar momentum-extreme gate (rising + positive + at 100-bar low) never fires on any coin; rules not relaxed |
| cluchanix | ClucHAnix (Freqtrade): Heikin Ashi + BB(40,2σ) + EMA 3/50 + Fisher RSI + ROCR(28/168) gate, exact hyperopt constants | Nominal winner: +$126 combined, 10 trades, PF 1.64 — inconclusive; a 1m scalper ported unscaled to 1h barely fires |
| multi_timeframe_ema_agreement | BotLab filter: 1h EMA(9/21) cross taken only when the 4h EMA(9/21) pair agrees | Nominal winner: +$1,065 combined, 306 trades, PF 1.07 — HYPE-carried (+$1,849); BTC -$1,100, MaxDD -21.1%; ETH +$317 |
| statoasis_rule4_momentum | StatOasis Rule 4: RSI(14)>55 + Stoch %K>50 + Williams %R>-50 + 120h return>1%, fixed 10-bar exit | Worst by dollars: -$2,663 combined, 1,026 trades, PF 0.94 — fees $7,193 = 2.7x the net loss; win rate collapsed from the source's 69.2% SPY-daily to 41.9% |
| minervini_trend_template | Minervini Trend Template: 8-condition SEPA gate + breakout from a tight base | Nominal winner: +$60 combined, 63 trades, PF 1.04 — breakeven noise; ETH +$435 the only green coin-leg of substance; 52-week gate uses the expanding trailing high/low (window < 52 weeks) |
| statoasis_rule5_short_fade | StatOasis Rule 5: RSI(14)>70 + Williams %R>-10 + falling SMA(100), fixed 5-bar exit | Nominal winner: +$315 combined, 44 trades, PF 1.21 — BTC +$781 (70.6% win, PF 3.43) echoes the source's OOS; ETH/HYPE replay its in-sample loss; fees $443 exceed the net profit |
| buyable_gap_up | Morales & Kacher Buyable Gap-Up: open gaps >=0.75xATR(40) above prior close on >=1.5x average volume | Nominal winner: +$1,317 combined, 10 trades, PF 2.63 — inconclusive, thin sample by design (1h gaps are rare in 24/7 crypto); best per-trade in batch (+$131.67) but n=10 |
| funding_fade | Negative-funding fade: long the moment Hyperliquid funding turns negative, 8h hold | Loser: -$878 combined, 548 trades, PF 0.96 — BTC/ETH both negative (Sharpe < -0.8); HYPE +$1,763 alone positive; funding income not modeled (8h leg ~0.01–0.04% of notional vs 0.11% round-trip fees) |
| weekend_momentum | Weekend effect: 168h momentum long/short gated to Fri 00:00 – Sun 23:59 UTC sessions | Nominal winner: +$1,210 combined, 105 trades, PF 1.30 — 35 trades/coin, modestly positive on all three coins; contested anomaly, thin sample; the stateless variant lost -$16,076 on stop-out churn (documented, not shipped) |
| ict_inducement_sweep | ICT sequence: inducement → sweep into the POI → MSS + displacement/FVG → 70.5% OTE entry | No trades: 0 combined, 0 trades — the full sequence never completes: 4 setups reach MSS+displacement, 0 reach the 70.5% OTE retracement within 24 bars; rules not loosened |

## Empirical direction (batch 43)

Combined batch print: +$2,719 across 2,311 trades (+$1.18/trade, PF 1.03) — the first net-positive batch (batches 34–42 were all combined-negative; batch 42: -$110,216). Read it straight: the print is HYPE-dependent, not a turn in the regime. HYPE legs sum +$6,997 while BTC (-$3,491) and ETH (-$787) are both red; seven nominal winners, three losers, two no-trade — and no robust winner among them. Every winner is thin (<=140 trades except multi_timeframe_ema_agreement), HYPE-carried, or both: btc_breakout_trend_climber's +$2,322 is 94% HYPE, buyable_gap_up's +$1,317 is 10 trades, cluchanix's +$126 is 10 trades, minervini_trend_template's +$60 is breakeven noise. Gross +$19,180 before $16,461 in fees — the fee schedule still takes 86% of the gross. BTC is green in 4 of 12 strategies (rule5 +$781, bgu +$540, weekend +$454, cluchanix +$5), ETH in 7 of 12, HYPE in 7 of 10 traded. Failure modes: (1) timeframe ports that don't port — statoasis_rule4_momentum's daily 10-bar hold becomes 1h churn (1,026 trades, $7,193 in fees) and oliver_kell_ema_reclaim's daily 5–19% pullback band never binds on 1h (BTC 0 trades); (2) gates that never fire — squeeze_momentum's 100-bar momentum extreme and ict_inducement_sweep's 70.5% OTE retracement both produce 0 trades, and both were left unloosened rather than tuned into firing; (3) funding fade loses on the price leg — negative funding is not a buy signal on 1h crypto in this window (BTC/ETH Sharpe < -0.8); (4) the HYPE carry repeats — the batch's only reason for printing green is HYPE legs (+$6,997) outweighing BTC+ETH (-$4,278). Spec corrections surfaced: weekend_momentum ships a one-entry-per-weekend state machine (the stateless re-entry variant churns 786 trades to -$16,076); funding_fade's fundingHistory fetch needs 10-day chunks (the API caps at ~500 rows, 30-day chunks silently left ~220h gaps) and hour-floored timestamps; cluchanix's alternative entry path (`ha_close < 0.00799 x lower band`) can never hold for positive prices — implemented as written, not repaired; the ROCR gate threshold 0.54904 is near-dormant because TA-Lib ROCR is a ratio ~1.0; squeeze_momentum's exit is the first momentum downtick, not a threshold cross. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795269600000), 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC; BTC/ETH 6,040 bars, HYPE 6,038) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin; combined PFs computed independently from the aggregated trade frames. Full new test suite: 180 tests green.

## Batch 44 — 2026-11-23

| Strategy | Mechanism | Combined result |
|---|---|---|
| hull_ma_trend | Hull MA(16) trend + HMA(64) filter (Alan Hull, 2005) | Loser: -$17,329 combined, 2,656 trades, PF 0.68 — worst by dollars; BTC MaxDD -71.8%, HYPE -$4,010 the least-bad leg; HMA's speed just means faster whipsaw entries |
| t3_ma_trend | Tillson T3(10, 0.7) + T3(30) agreement | Loser: -$10,456 combined, 1,383 trades, PF 0.74 — loses on all three coins; the lag-reduced EMA stack still crosses late and exits later |
| fisher_transform_trend | Ehlers Fisher Transform 0-cross (10-bar normalization) | Loser: -$15,322 combined, 1,970 trades, PF 0.67 — BTC -$6,752, Sharpe -6.23; the Gaussianized 0-cross fires on noise, not turns |
| ehlers_instantaneous_trend | Ehlers Instantaneous Trendline, alpha 0.07 | Loser: -$16,412 combined, 2,301 trades, PF 0.72 — second-worst by dollars; BTC MaxDD -71.8%; alpha ported unscaled from the daily book |
| keltner_macd_combo | Keltner(20, 1.5) breakout + MACD histogram agreement | Loser: -$8,795 combined, 1,084 trades, PF 0.69 — ~90% of trades exit on the signal within 1–2 bars (close back inside the channel almost immediately); gross -$1,527 before fees, so it loses even at zero fees |
| adx_dmi_trend | Wilder ADX(14) > 25 gate + DI cross | Loser: -$1,360 combined, 278 trades, PF 0.88 — gross +$794 before fees, a no-edge-after-fees system, not a broken mechanism; BTC +$1,609 (PF 1.40) is a single-coin artifact, not corroborated by ETH/HYPE |
| wilder_parabolic_sar | Raw Wilder PSAR(0.02, 0.2) flips, no MACD filter | Loser: -$6,273 combined, 1,466 trades, PF 0.90 — thinnest loser by PF; HYPE -$608 near breakeven; the raw flip system grinds steadily, no blowout leg |
| rsi_ema_pullback | RSI(14) dip below 40 then reclaim, EMA(50) uptrend filter | Inconclusive: -$158 combined, 3 trades — the reclaim gate almost never fires in an EMA(50) uptrend on 1h (BTC 2, ETH 1, HYPE 0); a 3-trade sample is not a verdict on the method; rules not loosened |
| donchian_turtle_breakout | Turtle System 1: 20-bar breakout, 10-bar exit, 2N stop | Loser: -$838 combined, 510 trades, PF 0.97 — thinnest loser by dollars and the closest to a real edge; ETH +$1,006 and HYPE +$46 green, BTC -$1,889; the skip rule was omitted (documented deviation) |
| macd_rsi_divergence | MACD histogram divergence on confirmed (±2-bar) pivots | Nominal winner: +$50 combined, 402 trades, PF 1.00 — exact breakeven noise (gross win $20,657 vs gross loss $20,607); ETH +$921 and HYPE +$1,189 green, BTC -$2,060; not a robust winner |
| stochastic_bollinger | Stoch(14,3,3) %K/%D cross at Bollinger %b extremes | Loser: -$7,816 combined, 815 trades, PF 0.68 — worst expectancy in batch (-$9.59/trade); the double-oversold gate buys continuation, not the turn |
| vwap_session_breakout | UTC-day session VWAP ±1.0 SD breakout, no ADX filter | Loser: -$7,600 combined, 1,232 trades, PF 0.82 — HYPE +$745 the only green leg; the UTC-midnight session anchor is the adaptation, 24/7 crypto has no true open |

## Empirical direction (batch 44)

Combined batch print: -$92,309 across 14,100 trades (-$6.55/trade, PF 0.78) — the fourth-worst batch by dollars (batch 34: -$126,826; batch 42: -$110,216; batch 41: -$95,275) and the second-worst per-trade (batch 41: -$8.83). Batch 43's first net-positive print (+$2,719) does not carry: this batch is back to all-loser except one exact-breakeven (+$50, PF 1.00) and one 3-trade inconclusive. Gross -$4,884 before $87,425 in fees — the fee schedule is ~18x the gross loss, so this batch is a fee story on top of a no-edge story. BTC is green in 1 of 12 strategies (adx_dmi_trend +$1,609 only), ETH in 3 of 12, HYPE in 3 of 12. Failure modes: (1) lag-reduced MAs still whipsaw — HMA, T3, Fisher and Instantaneous Trendline all lose with 1,383–2,656 trades each; removing lag does not remove the chop, it just enters it faster; (2) agreement filters agree too late — keltner_macd_combo's close is back inside the channel on ~90% of trades within 1–2 bars; (3) gates that never fire — rsi_ema_pullback's RSI-reclaim gate produces 3 trades in eight months and was left unloosened; (4) raw PSAR grinds — PF 0.90 but still -$6,273, the flip is the exit and the exit is the loss; (5) the Turtle is the nearest miss — PF 0.97, ETH/HYPE green, and the omitted skip rule is the one documented deviation that could plausibly matter. Spec corrections surfaced: the ADX gate can never fire on a single sustained ramp — the DI cross happens on the first trending bar, before ADX has built above 25, so entries only occur on later crosses inside an already-established trend (Wilder's rules as specified, not a bug); PSAR seeds LONG from bar 0 (SAR = low[0], EP = high[0]) and emits no entry on bar 0 — the first trade is the first genuine flip; the Turtle skip rule was omitted as specified; Fisher/Ehlers alpha 0.07 is ported unscaled from the daily book; base.rsi's 0-fill on flat stretches is suppressed by WARMUP. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795356000000), 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC; BTC/ETH 6,064 bars, HYPE 6,062) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin; combined PFs computed independently from the aggregated trade frames (two 0.1pp rounding diffs in MaxDD/net% display only). Full new test suite: 230 tests green.

## Batch 45 — 2026-11-24

| Strategy | Mechanism | Combined result |
|---|---|---|
| fakey | Nial Fuller Fakey: false break of an inside bar, close back inside the mother range | Loser: -$9,434 combined, 1,135 trades, PF 0.78 — negative gross of fees (-$2,244), no edge before costs; worst expectancy in batch (-$8.31/trade) |
| livermore | Livermore trend system: close above prior 20-bar high with higher swing lows | Loser: -$764 combined, 424 trades, PF 0.96 — thinnest loser by dollars; gross +$2,444 before fees, so the loss is cost-driven; ETH +$801 the only green leg |
| pi_cycle | Philip Swift Pi Cycle Top: long while SMA(111) < 2.0xSMA(350) | No trades: 0 combined — ratio peaked 1.22 vs the 2.0 trigger; untestable on 1h bars, not a bug |
| premium_discount | ICT premium/discount equilibrium: cross the 48-bar range midpoint after a discount/premium touch | Loser: -$1,987 combined, 816 trades, PF 0.94 — HYPE +$1,553 the only green leg; BTC -$2,966 |
| spinning_top | Nison spinning top reversal at 20-bar swing extremes | Loser: -$4,049 combined, 292 trades, PF 0.76 — a small body at an extreme is a pause in a continuing move, not a reversal |
| super_smoother_trend | Ehlers SuperSmoother(10) cross above SuperSmoother(30) | Loser: -$3,826 combined, 1,486 trades, PF 0.93 — gross +$6,302 before fees; HYPE +$3,237 the only green leg |
| three_bar_reversal | Joe Ross 3-bar reversal (hook) | Loser: -$7,688 combined, 982 trades, PF 0.81 — BTC Sharpe -4.70, MaxDD -59.9% |
| two_bar_reversal | Larry Williams 2-bar key reversal | Loser: -$7,382 combined, 1,175 trades, PF 0.84 — gross +$83 before fees, zero edge; HYPE +$212 is noise |
| ut_bot | QuantNomad UT Bot: ATR(10) trailing-stop trend system | Worst by dollars: -$12,325 combined, 2,008 trades, PF 0.81 — chop machine; BTC MaxDD -66.1% |
| heikin_ashi_stochastic | Heikin Ashi trend + Stochastic(14,3,3) cross at extremes | Loser: -$507 combined, 47 trades, PF 0.55 — tiny sample (~1 trade per coin per 5.5 days); long gate nearly shut by construction |
| ichimoku_stochastic | Ichimoku cloud + Tenkan/Kijun + Stochastic cross | Loser: -$2,471 combined, 223 trades, PF 0.49 — worst PF in batch; 211/223 exits are signal exits with a 2-bar median hold |
| gap_fill_fade | Gap-fill mean reversion: fade 1h gaps >=0.5 ATR toward the prior close | Scratch: -$29 combined, 25 trades, PF 0.98 — 25 trades proves nothing; gaps >=0.5 ATR barely exist on 24/7 1h crypto |

## Empirical direction (batch 45)

Combined batch print: -$50,462 across 8,613 trades (-$5.86/trade, PF 0.84, win rate 32.5%) — mid-pack on dollars (better than batch 44's -$92,309, batch 42's -$110,216, batch 41's -$95,275, batch 37's -$101,897, batch 36's -$111,363 and batch 34's -$126,826; worse than batch 43's +$2,719, batch 40's -$35,666 and batch 35's -$49,000) and mid-pack per-trade (better than batches 41, 37, 35, 36, 44, 42 and 40; worse than batch 34's -$5.23). No single global rank is claimed: the dated logs' ranking claims conflict (batch 37 called itself third-worst while ignoring batches 15/23), so the comparisons above are the verified ones. Gross +$6,370 before $56,832 in fees — the batch is gross-positive in aggregate and the fee schedule does the killing, the same shape as batches 40 and 44. Zero robust winners; 9 of 12 strategies are outright losers, 2 are thin-sample inconclusive (heikin_ashi_stochastic 47 trades, gap_fill_fade 25 trades), 1 is no-trade (pi_cycle). BTC is green in 0 of 12 strategies, ETH in 1 of 12 (livermore +$801), HYPE in 4 of 12 (super_smoother_trend +$3,237, premium_discount +$1,553, two_bar_reversal +$212, gap_fill_fade +$62). Failure modes: (1) reversal patterns that fade momentum lose — fakey, spinning_top, three_bar_reversal and two_bar_reversal all lose on every coin; the 1h tape continues through the pattern more often than it turns; (2) daily-bar regime indicators do not fire on 1h — pi_cycle's 2.0x trigger never approached (max ratio 1.22); (3) cloud-edge entries exit immediately — ichimoku_stochastic's median hold is 2 bars; (4) the fee story again — five strategies are gross-positive before fees (livermore +$2,444, premium_discount +$4,232, super_smoother_trend +$6,302, two_bar_reversal +$83, gap_fill_fade +$130) and still print red after the 0.055%/side round-trip. Spec corrections surfaced: heikin_ashi_stochastic ships Fast Stochastic (%K raw, %D = SMA(3)) — the "14,3,3" label conflicts with the formulas, and the formulas govern; ichimoku_stochastic omits Chikou Span (base.ichimoku's shift(-26) is a 26-bar lookahead — not computed or read); gap_fill_fade's ATR is taken at the gap bar (includes the gap bar's own true range), making the 0.5 ATR threshold slightly harder to clear than prior-bar ATR would; two_bar_reversal's shipped trigger requires a CLOSE above the pattern bar's high, stricter than Williams's original "trade above it"; ut_bot's KeyValue sweep (2.0: +$1,141 in-sample) was not adopted. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: 9 of 12 strategies are complete orphaned builds found in the local worktree (built ~Nov 14 on a stale window, never shipped) — verified, re-backtested on the batch-45 window, docs rewritten; 3 were skipped as near-duplicates of shipped strategies (head_and_shoulders ~ head_shoulders, pvo_percentage_volume ~ percentage_volume_osc, rsi_ema_cross ~ rsi_ma_cross) and replaced by 3 fresh builds. All 12 slugs were diffed against main's live API tree before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795525200000), 2026-03-14 22:00 UTC → 2026-11-24 14:00 UTC exclusive, last bar 13:00 UTC; BTC/ETH 6,111 bars, HYPE 6,109) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin; combined PFs computed independently from the aggregated trade frames. Full new test suite: 192 tests green.

## Batch 46 — 2026-11-25

| Strategy | Mechanism | Combined result |
|---|---|---|
| mesa_sine_wave | Ehlers MESA Sine Wave: Hilbert-transform sine/lead-sine cross | Worst by dollars: -$15,174 combined, 2,834 trades, PF 0.79 — the sine/lead-sine cross fires ~950x/coin on phase noise; BTC -$7,415 (Sharpe -5.95, MaxDD -76.0%) |
| tdi_traders_dynamic | Dean Malone TDI: RSI(13) + SMA(2/7) lines + BB(34, 1.6185) on RSI, 50-level filter | Loser: -$7,322 combined, 707 trades, PF 0.64 — worst win rate tier (28.6%); all three coins red |
| detrended_price_osc | DPO(20): close minus SMA(20) 11 bars back, zero-cross | Loser: -$8,949 combined, 1,398 trades, PF 0.81 — win rate 21.9%, the lowest in the batch; HYPE -$644 near breakeven, BTC -$5,087 |
| ppo_oscillator | Percentage Price Oscillator (12/26/9), signal cross gated on PPO sign | Loser: -$3,545 combined, 497 trades, PF 0.82 — thinnest loser by PF among the mid-pack; all coins red |
| stochastic_macd_combo | Stoch(14,3,3) extreme cross + MACD histogram agreement | Loser: -$1,518 combined, 73 trades, PF 0.42 — worst PF in batch and worst expectancy (-$20.80/trade); most selective (73 trades) yet worst per-trade |
| ichimoku_kumo_breakout | Kumo breakout: close through cloud + Tenkan>Kijun, exit back into cloud | Loser: -$6,846 combined, 540 trades, PF 0.68 — half its exits are 2xATR stops; breakout entries reverse immediately |
| kama_cross | Kaufman KAMA fast (ER 10) vs slow (ER 20) cross | Loser: -$1,302 combined, 696 trades, PF 0.96 — thinnest loser by PF; ETH +$228 and HYPE +$1,788 green, BTC -$3,319 |
| adx_bollinger_squeeze | Bollinger bandwidth squeeze + ADX(14)>20 band-break | Nominal winner: +$670 combined, 194 trades, PF 1.15 — best risk-adjusted in batch (Sharpe +0.59, MaxDD -3.6%, the only MaxDD under 10%); ETH +$820 the driver, BTC +$63 negligible, HYPE -$212 |
| donchian_rsi_combo | Donchian(20) breakout + RSI(14) filter, 10-bar Turtle exit | Nominal winner: +$642 combined, 536 trades, PF 1.02 — ETH +$1,411 and HYPE +$1,166 green, BTC -$1,935; breakeven-grade, not robust |
| ema_ribbon_cross | EMA 8/13/21/34/55 ribbon, full alignment after 20-bar compression | Loser: -$2,608 combined, 364 trades, PF 0.81 — ETH +$667 the only green leg; BTC PF 0.51 |
| coppock_curve_bull | Coppock Curve 1h-scaled (ROC 336+264, WMA 240): below-zero upward hook | Loser: -$1,712 combined, 262 trades, PF 0.84 — slow bleed; HYPE +$163 breakeven-positive, BTC/ETH both red |
| chaikin_vwap_combo | CMF(20) zero-cross + UTC-day VWAP agreement | Second-worst by dollars: -$12,368 combined, 1,350 trades, PF 0.62 — CMF zero-cross chop machine; BTC -$6,704 (Sharpe -7.84, MaxDD -67.4%) |

## Empirical direction (batch 46)

Combined batch print: -$60,032 across 9,451 trades (-$6.35/trade, PF 0.80, win rate 32.4%) — worse by dollars than batch 45 (-$50,462) and batch 40 (-$35,666), better than batch 44 (-$92,309), batch 42 (-$110,216), batch 41 (-$95,275) and batch 34 (-$126,826); worse per-trade than batch 45 (-$5.86) and batch 34 (-$5.23), better than batch 44 (-$6.55) and batch 41 (-$8.83). Gross +$3,720 before $63,752 in fees — the batch is gross-positive in aggregate and the fee schedule does the killing, the same shape as batches 40, 44 and 45. Two marginal nominal winners (adx_bollinger_squeeze +$670, PF 1.15; donchian_rsi_combo +$642, PF 1.02), neither robust — both are coin-dependent (green on ETH+HYPE, red or negligible on BTC) and small against their trade counts. Ten outright losers. BTC is green in 1 of 12 strategies (squeeze +$63, negligible), ETH in 4 of 12, HYPE in 3 of 12. Failure modes: (1) oscillator crosses fire on noise at 1h — MESA sine (2,834 trades), CMF (1,350) and DPO (1,398) all chop, and the MESA cross is the worst loser of the batch; (2) breakout entries reverse immediately — half of ichimoku_kumo_breakout's exits are 2xATR stops; (3) the fee story again — five strategies are gross-positive before fees and still print red after the 0.055%/side round-trip; (4) slow-indicator ports keep bleeding slowly — Coppock's 240h WMA is -$1,712 on 262 trades; (5) selectivity does not save a bad gate — stochastic_macd_combo fires only 73 times and still has the worst PF (0.42) and worst expectancy (-$20.80/trade) in the batch. Spec corrections surfaced: DPO ships the causal reading (close minus the SMA ending 11 bars back — StockCharts' centered plot subtracts an SMA ending 11 bars in the future, which is lookahead); the Donchian 10-bar Turtle exit is judged against the prior bars' channel (the unshifted 10-bar low includes the current bar's own low, so the close can never be below it and the exit could never fire); KAMA's ER-20 fast==slow sweep case is degenerate (0 trades, no cross possible); MESA's homodyne discriminator uses atan2 instead of Ehlers' arctan (same discriminator, correct quadrants); the Coppock WMA was initially weighted backwards and fixed to front-weighted (newest first); donchian signals take entry_n/exit_n parameters after the calibration sweep exposed a hardcoded-20 KeyError. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live API tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795615200000), 2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last bar 13:00 UTC; BTC/ETH 6,136 bars, HYPE 6,134) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin; combined PFs computed independently from the aggregated trade frames. Full new test suite: 164 tests green.

## Batch 47 — 2026-11-26

| Strategy | Mechanism | Combined result |
|---|---|---|
| the_strat | Rob Smith The Strat: 1/2/3 bar classification, 2-1-2 / 3-1-2 / 2-2 reversals + continuations, FTFC-gated on completed daily+weekly blocks | Loser: -$11,372 combined, 1,161 trades, PF 0.57 — BTC Sharpe -6.47, MaxDD -57.0%; signal exits outnumber stops ~4:1, positions flip on every counter-setup |
| ehlers_dominant_cycle | Ehlers band-pass filter (period 20, bandwidth 0.7), dominant cycle = 2x zero-crossing spacing, trade BP zero-crosses | Loser: -$11,784 combined, 1,939 trades, PF 0.82 — the cycle measurement validates (sine tests recover periods 20/40 within ±20%); trading its zero crossings is the problem |
| ehlers_universal_osc | Ehlers two-pole band-pass oscillator (period 20, bandwidth 0.3) + AGC, trade BP/trigger crosses | Second-worst by dollars: -$19,996 combined, 2,718 trades, PF 0.66 — BTC -$7,941 (Sharpe -6.50, MaxDD -80.8%); the shipped trigger scale 0.9 is the worst of its own sweep |
| dynamic_momentum_index | Chande & Kroll DMI: TD = clamp(int(14/Vi), 5, 30), simple-mean RSI over TD; cross 30/70, exit 50 | Loser: -$9,873 combined, 1,019 trades, PF 0.71 — BTC -$5,541 (-55.4% of equity); ETH/HYPE both print 336 trades with identical exit splits (verified coincidence, not a data bug) |
| connors_tps | Connors TPS: SMA(200) trend, RSI(2) < 25 / > 75 two bars, exit RSI(2) > 70 / < 30 or 10-bar time exit | Loser: -$7,355 combined, 974 trades, PF 0.69 — 58.0% win rate that still loses (small wins, larger losses); the daily→1h scaling is the prime suspect |
| williams_r_divergence | Williams %R(14) divergence on confirmed (±2-bar) pivots, gates -80/-20, exit -50 cross | Loser: -$4,769 combined, 189 trades, PF 0.41 — worst expectancy in batch (-$25.23/trade) and worst win rate (27.0%); smallest dollar loss only because it trades least |
| ict_ote_entry | ICT OTE: sweep + displacement + MSS, enter on retracement into the 62–79% zone | Nominal winner: +$366 combined, 8 trades, PF 2.03 — meaningless: 8 trades in 8.5 months, all 8 exited on the stop (0 signal exits) |
| ict_killzone | ICT killzones (London 07:00–10:00 UTC, NY 12:00–14:00 UTC): sweep Asian range + displacement, enter at 50% of the leg | Nominal winner: +$10 combined, 2 trades, PF inf — two trades in eight months, both exited on max hold; setups armed on 72 bars but only 2 ever reached the entry |
| rsi_vwap | RSI(14) cross through 30/70 with close on the right side of session VWAP, exit at RSI 50 / VWAP cross | Loser: -$347 combined, 128 trades, PF 0.91 — win rates 24–28% everywhere; HYPE +$638 the only green leg |
| heikin_ashi_adx | Heikin Ashi trend + ADX(14) > 25 + DI agreement (level condition, not a cross) | Loser: -$17,962 combined, 1,624 trades, PF 0.51 — combined equity ends $12,035 on $30k; the level-condition entry re-fires on every bar of a persistent run |
| supertrend_vwap | Supertrend(10, 3) + session VWAP agreement (level condition, not a cross) | Worst by dollars: -$23,112 combined, 2,419 trades, PF 0.54 — combined equity ends $6,887 on $30k; BTC Sharpe -8.23, MaxDD -87.5% |
| donchian_stochastic | Donchian(20) breakout + Stoch(14,3,3) filter (%K > %D, %K < 80), Turtle 10-bar exit | Nominal winner: +$168 combined, 61 trades, PF 1.10 — noise: the entire profit rests on HYPE's 8 trades (+$405); BTC/ETH both lose; the %K gate only passes on wick breakouts, hence 61 trades vs 536 for the RSI combo |

## Empirical direction (batch 47)

Combined batch print: -$106,027 across 12,242 trades (-$8.66/trade, PF 0.66, win rate 32.1%) — third-worst batch by dollars (batch 34: -$126,826; batch 42: -$110,216) and second-worst per-trade (batch 41: -$8.83). Gross -$41,578 before $64,449 in fees — this batch loses even at zero fees, so unlike batches 40, 44, 45 and 46 it is NOT a fee story, it is a no-edge story. Three nominal winners (ict_ote_entry +$366 on 8 trades, ict_killzone +$10 on 2 trades, donchian_stochastic +$168 on 61 trades), none robust — all three are thin-sample artifacts, and the two ICT positives are untestable at 8 and 2 trades. Nine outright losers. BTC is green in 1 of 12 strategies (killzone +$4.49, one trade), ETH in 2 of 12 (ote +$113, killzone +$5.35 — both negligible), HYPE in 3 of 12 (ote +$367, rsi_vwap +$638, donchian_stochastic +$405). Failure modes: (1) level-condition entries re-fire every bar — HA+ADX and Supertrend+VWAP were specified as levels, not crosses, and churn 1,624 / 2,419 trades into -$41,074 combined; (2) Ehlers cycle oscillators fire on phase noise — the two Ehlers builds combine for -$31,780 on 4,657 trades; (3) ICT setups almost never fire on 1h — the killzone's own 4-bar sequence cannot fit inside its 2–3-bar windows, and OTE needs a sweep+displacement+retracement chain that completes 8 times in 8.5 months; (4) selectivity does not save a bad gate — williams_r_divergence fires 189 times with the worst expectancy (-$25.23/trade) and worst win rate (27.0%) in the batch; (5) high win rate is no rescue — connors_tps wins 58.0% of its trades and still loses -$7,355. Spec corrections surfaced: the_strat exits are the opposite setup (the brief specified entries only) and its FTFC gate uses completed 24h/168h blocks; Ehlers' HP detrender cutoff derives as 61.5 bars (one octave below the 30.8-bar lower pass-band edge); the universal oscillator's AGC uses an expanding RMS until 100 bars accumulate; DMI uses simple-mean RS over TD, not Wilder smoothing (no canonical Wilder form exists over a changing window); TPS is scaled to 200 1h bars with the house stop added where the original has none, and max_hold 10 enforces the book's day-11 time exit; Williams' pivot machinery is taken from macd_rsi_divergence; the killzone windows include their end-hour bar and an armed setup's entry may land after the window closes (the sequence cannot fit otherwise); both ICT builds freeze the near swing at the back-inside bar for the MSS break and re-anchor the sweep clock on each new sweep extreme; donchian_stochastic's %K gate only passes on wick breakouts; rsi_vwap's base.rsi 0-fill jump sits inside WARMUP only. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 12 slugs were diffed against main's live API tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795701600000), 2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last bar 13:00 UTC; BTC/ETH 6,160 bars, HYPE 6,158) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin; combined PF computed independently from the aggregated trade frames (12,242 trades, 3,931 wins, 32.1%). Full new test suite: 195 tests green.

## Batch 48 — 2026-11-27

| Strategy | Mechanism | Combined result |
|---|---|---|
| alligator_awesome_combo | Bill Williams Profitunity: Alligator SMMA 13/8/5 (unshifted) + AO + fractal breakouts | Loser: -$7,314 combined, 678 trades, PF 0.70 — fractal breakouts keep failing on 1h crypto; BTC -$3,081 (Sharpe -2.72, MaxDD -33.6%) |
| keltner_mean_reversion | Keltner EMA20 ± 2xATR(10) fade + candle-direction filter | Zero trades: 0 of 381 lower-band crosses are bullish candles and 0 of 363 upper crosses are bearish — on 24/7 crypto the open chains to the prior close, so a cross-below bar is bearish by construction; diagnostic without the filter fires 592 trades and still loses -$5,296 |
| atr_expansion_breakout | Crabel NR7: narrowest range of 7, bracket breakout, 3-bar validity | Worst by dollars: -$17,359 combined, 1,734 trades, PF 0.65 — ~1,050 NR7 bars per coin: the narrowest range of 7 is routine on 1h, not a rare contraction; 1,095 of 1,734 trades die on the signal exit |
| wyckoff_accumulation | Wyckoff accumulation: spring + SOS + LPS, long only | Loser: -$1,998 combined, 118 trades, PF 0.69 — the chain is rare as it should be (29/24/82 springs), but 100 of 118 trades exit on the 2xATR stop; the spring low sits almost on top of the entry |
| mtf_macd_confirmation | Elder Triple Screen: 1h MACD cross gated on 4h MACD histogram sign | Loser: -$3,733 combined, 504 trades, PF 0.82 — all three coins red; HYPE -$465 the least-bad |
| funding_rate_carry | Directional funding carry: short extreme-positive / long extreme-negative 24h avg funding | Loser: -$931 TOTAL combined (price -$980 + funding +$49), 43 trades, PF 0.57 — the carry leg works (funding positive on all three coins) but ~$1/trade of funding is swamped by -$20–35/trade price expectancy; 35 of 43 trades end on the stop |

## Empirical direction (batch 48)

Combined batch print: -$31,335 across 3,077 trades (-$10.18/trade, PF 0.70, win rate 28.4%, Sharpe -4.65, MaxDD -17.6% on the $180k combined curve) — the worst per-trade of batches 11–48 (previously worst was batch 41 at -$8.83/trade, per the parent-verified ranking of batches 11–47); by dollars it is well clear of the worst (batch 34: -$126,826). Gross -$12,652 price PnL before $18,732 in fees, funding adds +$49 — this batch loses even at zero fees, so like batch 47 it is NOT a fee story, it is a no-edge story. Zero robust winners and one zero-trade strategy (keltner); five outright losers. BTC is green in 0 of 6 strategies, ETH in 0 of 6, HYPE in 0 of 6 (on TOTAL PnL; the funding carry leg itself is green on all three coins, +$14/+$9/+$26). Failure modes: (1) volatility-contraction brackets churn — NR7 fires ~1,050 times per coin and the breakout pokes out then falls straight back through the arming level in 1,095 of 1,734 trades; (2) fractal breakouts fail on 1h crypto — the Alligator system loses on all three coins with gross -$2,475 before fees; (3) a canonical filter can be structurally unfireable — the Keltner candle-direction rule never coincides with a band cross because the open chains to the prior close; (4) Wyckoff springs give no room — the spring low sits almost on top of the entry, so 100 of 118 trades hit the 2xATR stop; (5) funding carry is real but tiny — +$49 across 43 trades (~$1/trade) against -$21.64/trade total expectancy. Spec corrections surfaced: the Alligator ships unshifted SMMA (the book's 8/5/3-bar forward displacement is a plotting convention — using it causally would be lookahead); the NR7 armed columns are set on the NR7 bar itself (a close cannot cross its own bar's high, so no added entries); the Wyckoff dip is measured against the range low before the dip bar (the current bar's low is inside the rolling 120-bar window, so low < range_low could never be true otherwise); funding thresholds come from the pooled 90th percentile of positive 24h avg funding (0.0000125/hr) fixed before any PnL was seen; the 4h MACD gate uses completed 4h bars only via the new strategies/timeframes.py helper; funding TOTAL is computed by adding per-trade funding accrual at each trade's exit bar. No parameters were tuned to PnL. Per-coin detail lives in each strategy's BACKTEST.md / CALIBRATION.md.
Process note: all 6 slugs were diffed against main's live API tree via the API before building; no duplicates. Backtest numbers were re-run by the coordinator on the final shipped code on the fixed window (t in [1773525600000, 1795788000000), 2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last bar 13:00 UTC; BTC/ETH 6,184 bars, HYPE 6,182) and matched every builder's numbers exactly — net PnL, trades, win rate, Sharpe, expectancy, PF and MaxDD cross-checked per coin; combined PF/win rate/Sharpe/MaxDD computed independently from the aggregated trade frames (3,077 trades, 875 wins, 28.4%). Full new test suite: 105 tests green. Funding cache extension hit Hyperliquid 429 / RemoteDisconnected errors and needed retries (BTC on the first attempt, ETH/HYPE via 1-day chunks); candle cache extended to 1795788000000 with no failures. All 36 commits landed cleanly on the first attempt (no 422/500s this run).
