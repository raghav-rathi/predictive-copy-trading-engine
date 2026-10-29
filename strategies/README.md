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
