# Order Flow Imbalance — Calibration

All parameters fixed a priori from the footprint-delta
mechanism in the batch brief. No in-sample sweep, nothing
selected on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Bar delta | v * (c - o) / max(h - l, eps), clipped to [-v, v] | the brief's OHLCV proxy for footprint delta: close position inside the range signs the volume |
| Imbalance window | 5 bars, sum(delta) / sum(volume) | short enough to catch pressure shifts, long enough that one bar cannot max it out alone (one full bar moves it by at most 0.2) |
| Long threshold | cross above +0.25, close > EMA(20) | +0.25 = a quarter of window volume net buying; the EMA filter keeps entries with the short trend |
| Short threshold | cross below -0.25, close < EMA(20) | symmetric |
| Exit | imbalance crosses back through 0 | the pressure that justified the trade is gone; no fixed target |
| EMA | 20 bars | canonical short-trend filter |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house standard |
| Target | none | the zero-cross manages the trade |
| Max hold | 120 bars (~5 days) | backstop only; zero-cross exits dominate in practice |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Proxy disclosure (not tuning):** true footprint delta
classifies each trade at the bid or ask; this strategy
cannot do that from OHLCV data and does not pretend to.
The (c - o) / range proxy was chosen on mechanism (close
location inside the range is the only aggression hint a bar
carries), not on backtest results, and its weakness is the
leading explanation for the backtest outcome: on 1h bars the
proxy fires on range position, which mean-reverts, while the
entry rule bets on continuation.

**Verdict: loser.** -$10,996 combined over 1,424 trades
(30.5% win rate). Do not trade this as shipped.
