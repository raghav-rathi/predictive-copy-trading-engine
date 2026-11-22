# BTC Breakout Trend Climber — Calibration

All parameters were fixed **a priori** from the published source
and 1h-bar reasoning — there is no in-sample sweep, so there is
nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Donchian lookback | 600 bars (25 days) | the source's 25-day highest high, mapped bar-for-bar to 1h |
| Bollinger Band | 50-period, 2.1σ, EMA mid | the source's band; EMA mid is the source's construction, not the house SMA default |
| Entry | cross above prior-600 high OR above upper BB (mirror for shorts) | the source's OR entry, mirrored for shorts (the source is long-only) |
| ATR windows | 5 / 15 / 10 in the source; 10 in the harness | see deviation below |
| Stop / trail | 3.5xATR / 11.0xATR | the source's stop distance and trail distance |
| Target / max hold | none / none | the source exits only on the stop/trail |
| Risk | 1% / trade, 3x leverage cap | house standard |

## Documented deviation: single-ATR-window mapping

The source's exit is ATR-staged across three windows: initial
stop at entry − 3.5xATR(5); once price rises 1xATR(15) above
entry, trail 11xATR(10) below the last price. `RiskConfig`
carries a single ATR window, so the shipped mapping uses
ATR(10) for both the stop and the trail (stop 3.5xATR(10),
trail 11.0xATR(10)). The staged trigger (trail arms only after
+1xATR(15)) is likewise not expressible — the harness's
chandelier trail is live from entry, but with an 11xATR trail
distance it cannot bind until price has run more than 7.5xATR
above entry, which approximates the source's late-arming
behaviour. The 5-vs-10 stop-window difference is second-order:
on 1h crypto ATR(5) and ATR(10) are close, and the 3.5x
multiple dominates the stop distance either way.

The long-only source is mirrored for shorts: a short breakout
is the exact reflection of the long breakout (prior-600 low /
lower BB), with the same stop/trail distances. No parameter was
tuned on the backtest window.
