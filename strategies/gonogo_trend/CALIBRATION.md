# GoNoGo Trend — Calibration

## Shipped parameters (a priori, from the published checklist)

EMA 9/21/50, MACD 12/26/9, ADX(14) with a 20 threshold, Donchian
50, RSI(14), oscillator z-window 50, clamp ±6, state thresholds
±4 (strong) / ±2 (weak). None of these were chosen from the
backtest: they are the standard published values for each
component, and the ±4/±2 state bands follow directly from the
brief's state definitions. No parameter was tuned to PnL.

## Max-hold sweep (the only sweep run)

Same signals, same costs/sizing, max_hold_bars 100 / 150
(shipped) / 200, Hyperliquid 1h BTC/ETH/HYPE over the batch
window:

| Max hold | BTC | ETH | HYPE | Combined |
|---|---|---|---|---|
| 100 | 332t, -$4,546 | 373t, -$3,548 | 305t, +$590 | 1,010t, -$7,505 |
| 150 (shipped) | 332t, -$4,546 | 373t, -$3,548 | 305t, +$590 | 1,010t, -$7,505 |
| 200 | 332t, -$4,546 | 373t, -$3,548 | 305t, +$590 | 1,010t, -$7,505 |

Identical to the dollar: the max-hold cap never binds. Exit
reasons on the shipped run are 603 signal exits vs 407 stops and
0 max-hold exits — every position ends by state flip or by the
2xATR stop before 100 bars. The 150-bar hold is therefore dead
weight in the config, kept only because the brief specifies it;
it changes nothing on this window. (On a slower timeframe or a
stickier state regime it might bind; on 1h crypto it does not.)

## What was NOT swept

The score weights (equal by construction), the ADX 20 threshold,
and the ±4/±2 state bands were not swept: sweeping them after
seeing a −$7,505 combined result would be in-sample rescue work
on a reconstruction whose vendor ground truth is unknown anyway.
If this engine is ever revisited, the first experiment should be
entry on strong-Go only (state +2) rather than any Go — the weak-Go
transitions are the most numerous and, by the 25% win rate, the
least reliable — but that change needs out-of-sample evidence,
not a tweak to this window.

## Implementation notes

- Early versions of `gonogo_score` let `np.where` turn NaN
  comparisons into 0.0, faking a neutral score during spin-up.
  Fixed by masking score/state to NaN until EMA(50) and
  Donchian(50) are formed (bar 49); the oscillator is NaN until
  bar 82 (z-window 50 on the MACD histogram). WARMUP=80 covers
  the score; oscillator-gated entries are additionally self-gated
  by NaN until bar 82.
- `into_go` is defined both as `(state >= 1) & (prev <= 0)` and
  via `crossed_above(state, 0)`; on integer states −2..+2 the two
  are identical — the cross check is kept as the canonical form.
