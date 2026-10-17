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
