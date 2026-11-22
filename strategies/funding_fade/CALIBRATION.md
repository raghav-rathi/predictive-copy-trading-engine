# Negative-Funding Fade — Calibration

All parameters were fixed **a priori** from the published Jlabs
model and 1h-bar reasoning — there is no in-sample sweep, so there
is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Entry trigger | first bar funding_rate < 0 after a bar >= 0 | the source's turn-negative event; entering on every negative bar would re-enter the same regime dozens of times, the turn is the discrete signal |
| Hold | 8 bars (8h) | Jlabs' winning hold: 8h beat 16h and 24h since 2020 (Sharpe 0.84, +227.67%, maxDD −14.77%, 14% time in market) |
| 7-day variant | NOT shipped | Janorium's "long while funding is negative, hold 7 days" is a different trade (regime hold + a week of funding harvest, not the turn); documented in README.md, not tested |
| Long only | allow_shorts=False | the source is long-only on negative funding; a short mirror (short when funding turns positive) is not the same thesis and is not supported by the source |
| ATR window | 14 | canonical |
| Stop | 2xATR | **deviation from source:** Jlabs' model has no stop-loss; the 2xATR stop is a house risk overlay against catastrophic 8h moves. It can only cut trades short, never extend them |
| Trail / target | None / None | the exit is the 8h clock; a trail or target would convert a fixed-hold trade into a different trade |
| Max hold | 8 bars | the real exit, matching the signal-level 8-bar exit |
| Risk | 1% / trade, 3x leverage cap | house standard |
| Warmup | 24 bars | one day of funding history so the turn test is meaningful |

The design bet is that a turn to negative funding marks crowded
shorts and the next 8 hours mean-revert up. The backtest
(BACKTEST.md) refutes the price leg of that bet on BTC/ETH in this
window (548 trades, combined −$878); the funding-income leg was
not modeled and is too small to plausibly reverse the verdict (see
BACKTEST.md Limitations).

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — e.g. lengthening the
hold until the sample looks good would be pure overfitting, and
would no longer be the Jlabs 8h model.
