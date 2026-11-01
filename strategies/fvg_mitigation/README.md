# FVG Mitigation

Smart Money Concepts fair value gaps: when price displaces so fast
that three consecutive bars leave a void — bar 3's low above bar 1's
high (bullish) or bar 3's high below bar 1's low (bearish) — the
market tends to retrace into that void before continuing. This
strategy trades the first retracement into the most recent gap.

## Mechanism

- Bullish FVG at bar i: low[i] > high[i−2]; the gap zone is
  [high[i−2], low[i]].
- Bearish FVG at bar i: high[i] < low[i−2]; the gap zone is
  [high[i], low[i−2]].
- Only the most recent unfilled gap per side is tracked; a gap is
  dropped once price closes through its far side, or after 200
  bars (stale).
- Each gap is used once: the first mitigation bar enters, later
  touches of the same gap do not re-enter.

## Entry / exit

- **Long entry:** first bar whose low dips into the open bullish
  gap while the close holds above the gap bottom.
- **Short entry:** first bar whose high pokes into the open bearish
  gap while the close holds below the gap top.
- **Exit:** close through the gap's far side (mitigation failed).
  The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar
  max hold.

## Source

- Fair Value Gap (SMC / ICT):
  https://www.trade-ideas.com/learning-center/trading-strategies/fair-value-gap-trading-strategy/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 20 bars
(3 bars to form a gap + ATR(14) + margin.).

## Honest limitation

On 1h bars, gaps form constantly and most are noise: overlapping
gaps from both sides fire conflicting signals, and the 'first
mitigation' rule enters into gaps that price is already filling
through. Without a higher-timeframe trend filter, this is a
mean-reversion bet on every retracement (see BACKTEST.md).

Paper only, no live execution.
