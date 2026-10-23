# SMI Ergodic Oscillator Crossover — Calibration

All parameters are **fixed a priori** to William Blau's published
SMI Ergodic values from "Momentum, Direction, and Divergence"
(1995) — ergodic smoothing 5/20, signal line 5, overbought/oversold
zones ±40. There was **no in-sample selection**: no parameter was
chosen, tuned, or confirmed against the backtest window. The
implementation in `indicators.py` exposes `fast`, `slow`, and
`signal_n` arguments purely as an API convenience; the shipped
strategy and every reported backtest use the Blau defaults, and no
sweep was run on this window.

Deliberately a priori choices carried over from the shared desk
conventions (not strategy-specific tuning):

- ATR(14) for the risk layer — the desk standard across all
  strategies.
- 1.5xATR hard stop / 2xATR chandelier trail — the desk's standard
  swing-trade risk frame; the 1.5x stop is the tight-ish end of the
  range because oscillator-cross entries in a ranging 1h market
  produce whipsaw tails.
- 96-bar (~4-day) max hold — keeps a stalled hook from tying up
  capital; a zone-hook that hasn't resolved in four days is a
  failed momentum turn.
- WARMUP=120 — double-EMA(5,20) spin-up plus signal-line spin-up,
  with margin (the oscillator is valid from bar 24; the margin
  keeps early-transition artifacts out of the trade set).

## One-line verdict

The shipped configuration is Blau's book, unoptimized. Any future
parameter work (different zones for the 1h crypto timescale, slower
ergodic pairs, asymmetric long/short zones) must be done on
walk-forward / out-of-sample data, never by re-selecting on this
window.
