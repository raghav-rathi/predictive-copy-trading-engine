# VWAP Std Bands — Calibration

All parameters fixed a priori from the session-VWAP
definition in the batch brief. No in-sample sweep, nothing
selected on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Session | UTC calendar day | crypto trades 24/7; the UTC day is the only session boundary available |
| VWAP | cumulative typical price x volume / cumulative volume, reset at UTC midnight | textbook session VWAP |
| Sigma | 20-bar rolling std of (close - VWAP) | the brief's specified practical proxy for the std of (typical price - VWAP) over the session so far; trailing window keeps it causal |
| Bands | VWAP +/- 1 sigma, +/- 2 sigma | 2 sigma marks the extreme excursion; 1 sigma is plotted for context, not traded |
| Long entry | breach of -2 sigma on the prior bar, close back above it this bar | requires both the excursion and the rejection, not a single-bar wick |
| Short entry | mirror at +2 sigma | symmetric |
| Exit | close reaches the VWAP midline | the mean-reversion target; no fixed ATR target |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house standard |
| Target | none | the midline manages the trade |
| Max hold | 120 bars (~5 days) | backstop only; a session trade should resolve within its day, and signal exits dominate in practice |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Proxy disclosure (not tuning):** the shipped sigma uses
close rather than typical price and a trailing 20-bar window
rather than the full session-so-far, exactly as the brief
specified. A full-session typical-price sigma would be
slower-moving and would widen bands later in the day; that
variant was not tested, and the choice was made on
definition, not on backtest results.

**Verdict: loser.** -$8,103 combined over 695 trades
(48.9% win rate, profit factor ~0.6). Do not trade this as
shipped.
