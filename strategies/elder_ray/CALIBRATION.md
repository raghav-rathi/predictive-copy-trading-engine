# Elder Ray — Calibration Note

## Parameters fixed a priori — no in-sample selection

Every numeric choice in this strategy is taken directly from the
published source, not from looking at backtest results:

| Parameter | Value | Source |
|---|---|---|
| EMA length | 13 | Elder's published constant (EMA(13) is the Elder Ray / Impulse baseline in *Trading for a Living*) |
| Exit rules | bear/bull power crossing 0; EMA slope reversal | Elder's documented trigger/exit logic (buy dips in uptrends, exit when the power that set up the trade exhausts or the trend breaks) |
| ATR window | 14 | risk-layer convention shared across the engine |
| stop_atr_mult | 1.5 | engine risk convention for mean-reversion-style swing entries |
| trail_atr_mult | 2.0 | engine risk convention |
| target_atr_mult | None | exits are signal-driven by design |
| max_hold_bars | 120 | ~5 days on 1h bars; stalled-position release |
| risk_frac / max_leverage / fees | 0.01 / 3.0 / HL taker | engine risk convention |

There was **no parameter sweep, no grid search, and no look at the
backtest numbers before fixing these values**. The BACKTEST.md
results below are therefore a genuine out-of-idea test of Elder's
published rules on 2026 Hyperliquid data — whatever they show,
winner or loser, stands as reported.
