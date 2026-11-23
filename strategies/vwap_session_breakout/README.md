# VWAP Session Breakout

A UTC-day session VWAP breakout: price breaking out of its own
session's value area, confirmed by volume. VWAP is the session's
volume-weighted fair price; the ±1.0 volume-weighted-SD band is
the session's value area. A close outside the band on
above-average volume is read as the session accepting a new
price — the breakout — and the trade rides it until price comes
back through VWAP.

## Rule (long)

```
close crosses above VWAP + 1.0 x session SD (transition)
AND bar volume > session average bar volume
```

- **Exit long:** close back below VWAP (the breakout failed /
  the session mean reclaimed price).
- **Short mirror:** close crosses below VWAP − 1.0 SD with
  above-average volume; exit short on a close back above VWAP.
- **Entries are transition-only:** the cross must happen on
  the entry bar; a held position never re-enters. An opposite
  entry condition while in a position flips it.
- **Entries only from the 3rd bar of a session onward:** on
  the first bars the SD is computed from 1–2 points (exactly 0
  on the first bar), so the band is not a meaningful breakout
  level yet. This is a degenerate-band guard, not a tuned
  parameter — see CALIBRATION.md.

## No ADX filter, by design

This is the same session-VWAP construction as the existing
`vwap_bollinger_bands` strategy, but with a 1.0-SD band and
WITHOUT its ADX(14) < 25 ranging-regime filter — that is the
point of this build. `vwap_bollinger_bands` *fades* the bands
in a ranging regime; this system *breaks out* of the bands with
no regime gate at all, to test whether the raw VWAP breakout
carries an edge on its own. It does not, on this window (see
BACKTEST.md).

## Honest flag: 24/7 crypto has no true session open

There is no market open, no overnight gap, and no institutional
open auction in crypto — the UTC-midnight anchor is an
adaptation, not a market structure event. Early in each UTC day
the VWAP and SD are computed from very few bars and are
correspondingly tight and noisy (hence the 3rd-bar guard), and
a "session" here is just a calendar slice. A breakout of a
band built from three bars of a calendar slice is a much weaker
statement than a breakout of a band built from a real session's
auction.

## 24-bar max hold: this is an intraday system on 1h bars

The 24-bar max hold is one full session. A breakout that has
not run within its own session is not a session breakout — it
is a position carried into a new session whose VWAP has reset
underneath it. On 1h bars that makes this an intraday system:
positions live hours, not days, and the backtest's ~400 trades
per coin (~1.6 per day) is the expected tempo, not overtrading.

## 1h scaling (documented)

- Session = one UTC calendar day = 24 hourly bars.
- Band width 1.0 SD (not the 2.0 of `vwap_bollinger_bands`):
  a breakout system needs a band price actually reaches, and
  1.0 SD is the level Shannon's VWAP work treats as the
  first value-area edge.
- Volume gate is the session's average bar volume through bar
  i (inclusive) — simple, causal, and documented in
  indicators.py.

## Risk

2×ATR(14) harness stop (the signal-level VWAP-reclaim exit is
the real exit), no trail, no target (there is no opposite-band
target in a breakout system), 24-bar (~one session) max hold,
1% risk per trade, 3× leverage cap. WARMUP = 24 bars (one full
session before the first signal can be trusted).

Source: Brian Shannon, *Technical Analysis Using Multiple
Timeframes* (2008), VWAP chapter
(https://www.alphatrends.net/).
