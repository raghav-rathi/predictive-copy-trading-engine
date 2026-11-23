# VWAP Session Breakout — Calibration

All parameters were fixed **a priori** from the published
specification and 1h-bar reasoning — there is no in-sample
sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Session anchor | UTC midnight | the only available session boundary in 24/7 crypto; an adaptation, not a market open (see README) |
| Band width | 1.0 × session volume-weighted SD | the first value-area edge in Shannon's VWAP work; a breakout system needs a band price actually reaches (vs the 2.0 of `vwap_bollinger_bands`, which is a fade system) |
| Volume gate | bar volume > session average bar volume | the breakout must be accepted on volume, not drifted through on thin bars; average is cumulative through bar i (inclusive) |
| Entry | close crosses the band (transition) | a close, not an intraday poke, above/below the band — the session must accept the new price at the close |
| Long exit | close back below VWAP | the breakout failed / the session mean reclaimed price |
| Harness stop | 2×ATR(14) | backstop only — the signal-level VWAP-reclaim exit is the real exit |
| Trail / target | none | no opposite-band target exists in a breakout system; a trail would fight the VWAP-reclaim exit |
| Max hold | 24 bars (one session) | a breakout that has not run within its own session is not a session breakout |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 24 bars | one full UTC session before the first signal can be trusted |

## Deviations and spec corrections surfaced while implementing

1. **Degenerate-band guard (builder-added, not in the spec).**
   On the first bar of a session the volume-weighted SD is
   exactly 0 (a single point has no variance), so the upper
   and lower bands coincide with VWAP and any close not equal
   to VWAP is technically "outside the band". Entries are
   therefore only considered from the 3rd bar of a session
   onward (`MIN_SESSION_BARS = 3`). This guards against a
   zero-width band; it is not a parameter tuned on the
   backtest window, and the backtest would be meaningless
   without it (session-open bars would fire on noise).
2. **No ADX filter, by design.** The spec explicitly removes
   the ADX(14) < 25 filter that `vwap_bollinger_bands` uses.
   The backtest shows the cost of that removal (see
   BACKTEST.md) — the regime gate was doing real work. It is
   not re-added here to rescue the numbers; that would be a
   different strategy.
3. **Volume gate uses the inclusive session average.** The
   spec says "the bar's volume above the session's average bar
   volume"; the average is computed through bar i inclusive
   (cum_v / bars_in_session), which is the simplest causal
   reading. A through-prior-bar average would differ only on
   bars where the current bar dominates the session average,
   and was not tried as an alternate.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 1.0-SD band width or the volume gate, which directly
control how many trades fire.
