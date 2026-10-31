# Chaikin Money Flow Zero-Cross

Volume-weighted accumulation/distribution oscillator traded on its
zero line: when the last 20 bars' volume-weighted closes sit in the
upper half of their ranges, money is flowing in (CMF > 0); when they
sit in the lower half, money is flowing out (CMF < 0).

## Mechanism

- **Money Flow Multiplier:** MFM = ((C − L) − (H − C)) / (H − L).
  It is +1 when the bar closes at its high, −1 at its low, 0 at the
  midpoint. When H == L the multiplier is defined as 0 (no range to
  locate the close in).
- **Money Flow Volume:** MFV = MFM × V.
- **CMF(20):** sum(MFV, 20) / sum(V, 20). Bounded in [−1, +1]. A zero
  volume sum over the window gives CMF = 0.

## Entry / exit

- **Long entry:** CMF(20) crosses above 0.
- **Short entry:** CMF(20) crosses below 0.
- **Exit:** the opposite zero cross. The risk layer adds a 2xATR stop,
  a 2.5xATR trail, and a 120-bar max hold.

## Source

- Chaikin Money Flow (CMF), Fidelity technical indicator guide
  (formula and zero-line interpretation verified via search):
  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmf
- Note: the StockCharts School CMF page (the canonical reference for
  this indicator) could not be fetched during this build (fetch
  failed), so the source_url above is the verified Fidelity page,
  whose formula — CMF = n-day sum of [(((C − L) − (H − C)) / (H − L))
  × Vol] / n-day sum of Vol — is identical. The 20-period window and
  the zero-cross rules are this strategy's own construction.

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage
per side, longs and shorts allowed. WARMUP = 25 bars.

## Honest limitation

A zero cross is a hair-trigger in a range: CMF whipsaws across zero
whenever closes alternate halves of their ranges, so this strategy
trades very often (1,900 trades across three coins in the backtest
window) and fees eat it alive — see BACKTEST.md. CMF also ignores
gaps entirely: a bar that gaps down and recovers to its own high
scores +1 even though price fell. Paper only, no live execution.
