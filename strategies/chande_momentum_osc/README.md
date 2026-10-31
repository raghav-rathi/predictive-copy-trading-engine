# Chande Momentum Oscillator

Chande Momentum Oscillator threshold strategy — a mean-reversion-flavored
momentum read: entries fire when the oscillator leaves an extreme zone,
exits fire when momentum fades to zero or re-enters the opposite extreme.

## Mechanism

- **CMO(14):** CMO = 100 * (UpSum - DnSum) / (UpSum + DnSum), where
  UpSum is the sum of positive close-to-close changes over 14 bars and
  DnSum is the sum of absolute negative changes over the same window.
  CMO ranges from -100 to +100. Unlike RSI, which averages gains and
  losses, CMO sums them, so it reacts to the raw balance of up vs down
  movement. A window with no price movement yields CMO = 0.
- **Levels:** +50 = overbought, -50 = oversold, 0 = momentum neutral
  (the source's standard levels).

## Entry / exit

- **Long entry:** CMO crosses above -50 (leaving oversold).
- **Short entry:** CMO crosses below +50 (leaving overbought).
- **Long exit:** CMO crosses below 0 OR crosses above +50.
- **Short exit:** CMO crosses above 0 OR crosses below -50.
- The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max
  hold.

## Source

- Chande Momentum Oscillator (Tushar Chande; formula, -100/+100 range,
  +50/-50 overbought/oversold levels):
  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
  (verified; the entry/exit threshold rules are this strategy's own
  construction, not the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 20 bars (CMO(14) needs 15 bars,
ATR(14) needs 14).

## Honest limitation

Leaving an extreme zone is not the same as a reversal: in a strong
trend CMO can leave -50 (or +50) and then fall straight back through
zero, which is exactly what the exit rules then do — the strategy
pays the round trip. The backtest (BACKTEST.md) shows all three coins
losing with signal exits at only ~40% of trades; the rest hit the stop.

Paper only, no live execution.
