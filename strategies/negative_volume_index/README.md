# Negative Volume Index

Paul Dysart's Negative Volume Index (Fosback's version): the
cumulative price change counted only on days when volume falls.
The thesis is that informed money moves quietly — on low-volume
bars — so the NVI trend against its 255-bar EMA reads the
smart-money direction.

## Mechanism

- NVI starts at 1000.
- If volume falls bar-over-bar: NVI *= (1 + price change %).
- If volume rises: NVI is unchanged.
- Signal line: EMA(255) of NVI. Above = quiet-money uptrend,
  below = quiet-money downtrend.

## Entry / exit

- **Long entry:** NVI crosses above its 255-bar EMA.
- **Short entry:** NVI crosses below its 255-bar EMA.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Negative Volume Index (Paul Dysart / Norman Fosback):
  https://www.daytrading.com/nvi

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 300 bars
(255 bars for the EMA(255) + ATR/margin.).

## Honest limitation

NVI was built for daily equity breadth; on 1h crypto bars volume
oscillates bar-to-bar, so roughly half the bars move the index and
the 'quiet money' premise dilutes. The 255-bar EMA is also very
slow, so crosses lag regime changes by days (see BACKTEST.md).

Paper only, no live execution.
