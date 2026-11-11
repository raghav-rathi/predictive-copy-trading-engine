# Vortex Squeeze

Vortex Indicator cross (Botes & Siepman, TASC Jan 2010) gated by a
Bollinger BandWidth squeeze: only trade a VI+/VI- cross while volatility
is compressed, or within 5 bars after the compression ends — the idea
being that squeezes precede the directional expansion that the cross
then confirms.

## Rules

- **Vortex:** VI+(14) / VI-(14), same formulas as `vortex`
  (VM+ = |h - l.shift(1)|, VM- = |l - h.shift(1)|, divided by the
  14-bar true-range sum).
- **Squeeze:** BandWidth(20, 2) = (upper - lower) / middle is below its
  own 120-bar 20th percentile.
- **Gate:** open while the squeeze is true, or within 5 bars after the
  squeeze ends.
- **Long entry:** VI+ crosses above VI- while the gate is open.
- **Short entry:** VI+ crosses below VI- while the gate is open.
- **Long exit:** VI+ crosses back below VI- (opposite cross).
- **Short exit:** VI+ crosses back above VI-.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

This is deliberately a squeeze-gated variant of the existing `vortex`
strategy (precedent: `ttm_squeeze`, `keltner_squeeze`): the plain
Vortex cross fires in all regimes, while this one only trades crosses
that follow volatility compression.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Botes & Siepman, Vortex Indicator (TASC Jan 2010): https://www.investopedia.com/terms/v/vortex-indicator-vi.asp
- Bollinger BandWidth squeeze concept: https://www.investopedia.com/terms/b/bollingerbands.asp

Paper only, no live execution.
