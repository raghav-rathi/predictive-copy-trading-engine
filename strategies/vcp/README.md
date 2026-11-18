# Volatility Contraction Pattern (VCP)

Minervini's Volatility Contraction Pattern: a base of shrinking
pullbacks (each shallower, each trough higher, volume drying up),
then a breakout above the pivot on expanding volume.

## Rules

- **Long entry:** a VCP base is valid AND the Stage-2 uptrend
  filter holds (close > SMA(50) AND SMA(50) > SMA(200)) AND the
  close breaks above the pivot (the high of the last contraction)
  AND volume expands (volume > 1.5x SMA(volume, 50)).
- **Short entry:** the symmetric mirror — a short base of
  successive rallies (each shallower, each peak lower, volume
  declining), downtrend filter (close < SMA(50) AND
  SMA(50) < SMA(200)), close below the pivot low, volume expansion.
  The short side is the symmetric extension of Minervini's
  long-only pattern, not part of the original.
- **Long exit:** the close falls back below the pivot (failed
  breakout) OR the opposite VCP signal prints.
- **Short exit:** the mirror.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 250 bars (SMA(200) needs 200 bars).

A pullback runs from a swing high to the following swing low
(causal 5-bar pivots, centre+2 confirmation); depth =
(high − low) / high. A base is valid when there are >= 2
successive pullbacks where each is shallower than the previous
(depth[k] < 0.95 * depth[k-1]), each trough is higher than the
previous trough, and mean volume on each down-leg is lower than on
the previous down-leg. A leg whose later low extends the same
starting swing high updates that leg in place rather than starting
a new leg. All computation is causal, so signals on bar i use only
data through bar i's close.

## Sources

- Quantum Algo, "VCP Pattern" —
  https://www.quantum-algo.com/blog/guides/vcp-pattern/
- TradePiko, "VCP Volatility Contraction Pattern" —
  https://www.tradepiko.com/blog/vcp-volatility-contraction-pattern

Paper only, no live execution.
