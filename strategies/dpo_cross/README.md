# DPO Cross

The Detrended Price Oscillator strips the long-term trend out of
price so the short cycle stands out: it compares the current close
with the 20-bar average displaced back 11 bars, and oscillates
around zero.

## Mechanism

- SMA(20) of close, displaced back 11 bars (20/2 + 1, the window's
  center point).
- DPO = close − displaced SMA(20). Positive means price sits above
  its centered trend; negative means below.
- Zero crosses mark the short cycle turning up or down.

## Entry / exit

- **Long entry:** DPO crosses above zero.
- **Short entry:** DPO crosses below zero.
- **Exit:** the opposite zero cross. The risk layer adds a 2xATR
  stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Detrended Price Oscillator (DPO):
  https://docs.prorealalgos.com/dpo.html

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 40 bars
(31 bars for the displaced SMA(20) + ATR/margin.).

## Honest limitation

DPO is a cycle tool, not a trend tool: in a strong trend it stays
on one side of zero for long stretches and its crosses cluster
around chop. The displaced average also means the oscillator
reacts to price structure 11 bars old (see BACKTEST.md).

Paper only, no live execution.
