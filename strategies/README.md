# Technical Strategy Library — batch 4 (2026-10-13)

Twelve real, tested, empirically-validated signal engines on
`feat/strat-iter-20261013-a`, merged from three build batches (a/b/c).
Each strategy is a self-contained subpackage:

    strategies/<slug>/indicators.py   -- indicator computation (pure pandas/numpy)
    strategies/<slug>/signals.py       -- entry/exit signal logic
    strategies/<slug>/risk.py         -- stops, trailing, targets, sizing config
    strategies/<slug>/test_<slug>.py  -- unit tests (green)
    strategies/<slug>/BACKTEST.md     -- empirical validation on Hyperliquid 1h candles
    strategies/<slug>/CALIBRATION.md  -- parameter sweep notes

Shared infra in this branch: `base.py` (signal conventions, indicator
primitives, `RiskConfig`/`StrategySpec`), `registry.py`, `data.py`
(Hyperliquid candle loader + disk cache), `backtest.py` (event-driven
harness: fees, slippage, funding; no lookahead), `tests/test_infra.py`.

Paper-first: everything runs on historical candles / paper signals only.
No live execution is wired anywhere in this package by design.

See STRATEGY_SUMMARY.md for the batch scorecard.

---

# Batch 5 (2026-10-14) — named-author classic-indicator sweep

Ten more signal engines on `feat/strat-iter-20261014-momentum`, all from
documented, named-author mechanisms: `coppock_curve` (E.S. Coppock),
`smi_ergodic` (Blau), `klinger_oscillator` (Klinger), `qstick` (Chande),
`rsi_bollinger` (Bollinger-on-RSI mean reversion), `cmf_trend` (Chaikin),
`chande_cmo` (Chande), `elder_ray` (Elder), `dpo_cycle` (ChartSchool),
`pgo` (Mark Johnson). Same subpackage layout; 510 tests green
(full suite incl. prior batches). Backtests on Hyperliquid 1h candles
(BTC/ETH/HYPE, 2026-03-20 → 2026-10-14): Coppock wins on HYPE (+50.2%,
Sharpe 2.61); the other nine lose — Qstick worst (−$17,746), RSI+Bollinger
the high-win-rate trap (47% WR, −$13,075). Honest losers recorded in
each BACKTEST.md.

Shared infra change in this batch: `base.crossed_above`/`crossed_below`
now accept scalar levels (broadcast to the series index); Series behavior
unchanged.

---

# Batch 8 (2026-10-17) — named-author classics + SMC mechanics

Twelve more signal engines on `feat/strat-iter-20261017-batch8`, all from
documented, named-author or published mechanisms: `momentum_pinball`
(Raschke LBR/RSI, Street Smarts), `tdi` (Dean Malone Traders Dynamic
Index), `half_trend` (everget HalfTrend ATR channel), `vidya` (Chande
VIDYA), `frama` (Ehlers FRAMA), `liquidity_sweep` (ICT stop-hunt fade),
`market_structure` (SMC BOS/CHoCH), `candle_patterns` (Nison engulfing +
pin bars), `linreg_channel` (Raff regression channel), `choppiness`
(Dreiss Choppiness Index + Donchian), `vwma_cross` (VWMA 20/50 + volume
gate), `ribbon_trend` (EMA 8/13/21/34/55 ribbon). Same subpackage layout;
63 new unit tests green. Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE,
2026-03-14 → 2026-10-17): rough batch — 7 losers, 4 mixed, 1 flat.
`market_structure` wins on HYPE (+32.0%, Sharpe 1.74, stable at (3,3)
pivots) and `ribbon_trend` prints HYPE +17.3% (+26.2% at stricter fan);
both bleed on BTC/ETH. `vwma_cross` HYPE +20.0% is flagged unstable (the
(10,30) sweep moves the edge to ETH). Honest losers recorded in each
BACKTEST.md, including the cost-arithmetic port failures (pinball, tdi,
candle_patterns) and the negative-skew liquidity_sweep (54-56% WR, −15%
to −24% net).

No shared infra changes in this batch.


---

# Batch 20 (2026-10-29) — oscillator crosses, pullbacks, ratio breakout, candle patterns

Twelve more signal engines on `feat/strat-iter-20261029-batch20`: `macd_bollinger`
(Bollinger on MACD), `cci_zero_cross` (CCI zero-line + trend filter),
`macd_histogram_reversal` (Elder histogram slope flips), `rsi_failure_swing`
(Cardwell failure swings), `stochastic_pop` (Raschke pop + breakout),
`keltner_pullback` (Keltner midline pullback), `ema_triple_cross` (3/8/21 EMA
stack), `relative_strength_breakout` (coin/BTC ratio-line breakout),
`abandoned_baby_pattern`, `kicker_pattern`, `tasuki_gap_pattern`,
`counterattack_lines` (Nison candle patterns). Same subpackage layout; 118 new
unit tests green. Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE,
2026-03-14 → 2026-10-28, with the three builder-C strategies run to
2026-10-27 13:00 UTC before a mid-batch cache extension): combined -$66,502
across 6,963 trades — 9 losers, 1 mildly-green noise print (tasuki +$238 on
42 trades), 2 no-evidence patterns (abandoned baby 0 trades, kicker 5).
The candle-pattern lane hits a structural wall on 24/7 hourly crypto: textbook
gap patterns assume an overnight close that does not exist here. Honest
losers recorded in each BACKTEST.md.

No shared infra changes in this batch.

# Batch 33 (2026-11-11) — Chande / Ehlers / Wilder / Bollinger / Connors sweep

Twelve more signal engines on `feat/strat-iter-20261111-batch33`, from
published, named-author mechanisms: `rwi` (Chande & Kroll Random Walk Index),
`voss_predictive_filter` (Ehlers Voss, TASC Aug 2019), `ehlers_early_onset_trend`
(Ehlers Quotient Transform, TASC Aug 2014), `ehlers_rsi` (Ehlers SuperSmoother
RSI), `connors_cumulative_rsi` (Connors cumulative RSI), `supertrend_ema_filter`
(Supertrend + EMA(200) regime filter), `macd_vwap_combo` (MACD + UTC-day VWAP),
`bollinger_w_bottom` (Bollinger W-bottom / M-top), `tema_cross` (TEMA 9/21),
`vortex_squeeze` (Vortex cross + BandWidth squeeze gate), `donchian_adx`
(Donchian 20 + ADX filter), `wilder_volatility_system` (Wilder Volatility
System, ATR(7) breakout). Same subpackage layout; 156 new unit tests green.
Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE, 2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC): combined -$28,551 across 9,166 trades — 9 losers, 3
nominally green. The only genuine winner is `wilder_volatility_system`
(+$3,758, 490 trades, Sharpe 1.20; HYPE +$2,804, ETH +$1,921, BTC -$967);
`supertrend_ema_filter` (+$1,205) and `connors_cumulative_rsi` (+$539) are
HYPE-carried / thin. Worst is `tema_cross` (-$10,514, 1,731 trades, $11,261 in
fees). Honest losers recorded in each BACKTEST.md.

No shared infra changes in this batch.

# Batch 37 (2026-11-16) — breadth proxies, cycle transforms, Dow/Elliott, volatility fades

Twelve more signal engines on `feat/strat-iter-20261116-batch37`: `mcclellan_oscillator` (McClellan breadth oscillator on candle-count RANA), `arms_index` (Arms TRIN), `demark_pivots` (DeMark conditional pivots), `jurik_rsx` (Jurik RSX reconstruction), `fft_dominant_cycle` (rolling-FFT dominant-cycle reconstruction), `wavelet_trend` (db4 wavelet approximation slope, pure-numpy DWT), `bayesian_changepoint` (Adams & MacKay BOCD), `volatility_quality_index` (Stridsman VQI), `dow_theory_trend` (Dow swing structure + volume), `elliott_wave_count` (strict 5-wave count), `schwager_volatility_ratio` (Schwager VR wide-bar fade), `prev_day_high_low` (prior UTC-day high/low breakout). Same subpackage layout; 227 new unit tests green. Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE, 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC): combined -$101,897 across 11,929 trades — zero green strategies; least-bad are `elliott_wave_count` (-$44, 34 trades) and `bayesian_changepoint` (-$403, 55 trades), both break-even noise. Worst is `volatility_quality_index` (-$20,285, 3,742 trades, $26,297 in fees); `mcclellan_oscillator` is worst per-trade (-$20.95). Honest losers recorded in each BACKTEST.md.

No shared infra changes in this batch.

# Batch 38 (2026-11-17) — indicator combos, breakouts, S/R flips, trendlines

Twelve more signal engines on `feat/strat-iter-20261117-batch38`: `heikin_ashi_macd` (Heikin Ashi + MACD histogram zero-cross, Raisontgh), `cci_macd_combo` (CCI(14) ±100 crosses confirmed by MACD), `triple_rsi` (RSI 7/14/21 full agreement), `volume_ma_breakout` (20-bar breakout + 1.5x volume), `swing_high_low_breakout` (5-bar pivot HH/HL structure breakout), `support_resistance_flip` (break-and-retest role reversal on 50-bar pivot levels), `trendline_breakout` (Demark-style trendlines through last two 10-bar pivots), `supertrend_rsi` (Supertrend(10,3) + RSI(14) 50-cross), `ichimoku_macd` (Ichimoku cloud + Tenkan/Kijun + MACD), `adx_ema_trend` (EMA 20/50 cross with ADX(14) > 25), `rsi_volume_confirmation` (RSI(14) 50-cross + 1.25x volume), `donchian_macd` (Donchian(20) breakout + MACD histogram). Same subpackage layout; 206 new unit tests green. Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE, 2026-03-14 22:00 UTC → 2026-11-17 14:00 UTC): combined -$56,719 across 8,649 trades — zero green strategies; least-bad are `ichimoku_macd` (-$254, 293 trades, PF 0.98) and `adx_ema_trend` (-$573, 76 trades, PF 0.82), both break-even noise. Worst is `triple_rsi` (-$11,465, 1,294 trades, BTC Sharpe -3.74); `swing_high_low_breakout` is worst by Sharpe (-3.50). Gross +$5,598 before $62,318 in fees — the entries roughly break even and the fee schedule does the killing. Honest losers recorded in each BACKTEST.md.

No shared infra changes in this batch.

# Batch 48 (2026-11-27) — Williams, Keltner, Crabel, Wyckoff, MTF MACD, funding carry

Six more signal engines on `feat/strat-iter-20261127-batch48`: `alligator_awesome_combo` (Bill Williams Profitunity: Alligator SMMA + AO + fractal breakouts), `keltner_mean_reversion` (Keltner EMA20 ± 2xATR fade + candle-direction filter — 0 trades: the filter never fires on 1h crypto), `atr_expansion_breakout` (Crabel NR7 bracket breakout), `wyckoff_accumulation` (Wyckoff spring + SOS + LPS, long only), `mtf_macd_confirmation` (Elder Triple Screen: 1h MACD cross gated on 4h MACD histogram), `funding_rate_carry` (directional funding carry: short extreme-positive / long extreme-negative 24h avg funding). Same subpackage layout; 105 new unit tests green (incl. 5 for the new `strategies/timeframes.py` 4h-resample helper). Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE, 2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC): combined -$31,335 across 3,077 trades (-$10.18/trade, PF 0.70) — worst per-trade of batches 11–48; zero green strategies, zero green coins in any strategy. Worst is `atr_expansion_breakout` (-$17,359, 1,734 trades, PF 0.65); least-bad is `funding_rate_carry` (-$931 TOTAL, 43 trades — the funding leg itself earns +$49 on all three coins, swamped by price losses). Gross -$12,652 before $18,732 in fees — loses even at zero fees, not a fee story. Honest losers recorded in each BACKTEST.md.

Shared infra changes in this batch: `strategies/timeframes.py` (UTC-aligned 1h→4h resample + MACD mapped from completed 4h bars only, no lookahead) with tests in `strategies/tests/test_timeframes.py`; `scripts/run_pinned_backtest48.py` (pinned-window driver); `scripts/extend_funding_cache48.py` (funding-cache extension in 1-day chunks with backoff, HL 429-safe).

# Batch 49 (2026-11-28) — Saucer, Popgun, FTD, day-of-week, vol estimators, Wyckoff distribution, ORB fade, streak fade, balance line

Ten more signal engines on `feat/strat-iter-20261128-batch49`: `ao_saucer` (Bill Williams AO Saucer: 3-column AO turn above/below zero), `popgun` (Kennedy Popgun: inside + outside bar, breakout of the outside bar's range), `follow_through_day` (O'Neil FTD: rally-attempt day 4–7, ≥1.5% day gain on higher volume — 7 trades, BTC 0), `day_of_week_effect` (Bitcoin day-of-week: long Mondays, short Thursdays — +$5,064, the batch's only real winner), `garman_klass_volatility` (Garman-Klass 1980 realized-vol expansion + EMA(20) direction), `parkinson_volatility` (Parkinson 1980 realized-vol expansion, same structure — beats GK by $1,857, HYPE +$1,734), `wyckoff_distribution` (Wyckoff UTAD + SOW + LPSY, short only), `orb_fade` (opening-range breakout failure fade), `streak_fade` (Connors consecutive-days fade: 60.1% win rate, still -$7,399), `balance_line_pullback` (Bill Williams Balance Line pullback to the Alligator jaw — worst by dollars, -$11,431). Same subpackage layout; 168 new unit tests green. Backtests on Hyperliquid 1h candles (BTC/ETH/HYPE, 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC): combined -$33,361 across 5,225 trades (-$6.38/trade, PF 0.83) — gross +$3,120 before $36,482 in fees, so the fee schedule does the killing; two nominal winners (day_of_week_effect +$5,064, PF 1.48; follow_through_day +$159 on 7 trades), eight outright losers. Worst is `balance_line_pullback` (-$11,431, 1,254 trades, PF 0.72); least-bad is `parkinson_volatility` (-$606, 424 trades, PF 0.96, gross +$2,407). Honest losers recorded in each BACKTEST.md.

Shared infra changes in this batch: `scripts/run_pinned_backtest49.py` (pinned-window driver).
