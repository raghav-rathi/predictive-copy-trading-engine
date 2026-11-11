# Early Onset Trend

John Ehlers' Early Onset Trend ("The Quotient Transform", TASC August
2014): an early trend detector built to reduce the lag of moving-average
trend indicators. A roofing filter strips out cyclic components with
periods longer than 100 bars (spectral dilation), a SuperSmoother(30)
strips out short-period noise, an automatic-gain-control peak tracker
normalises the result, and the quotient transform turns the normalised
value into an oscillator whose values near +1 mean uptrend and near −1
mean downtrend.

## Rules

- **Roofing filter:** 2-pole high-pass, 100-bar cutoff, on closes.
- **Smoother:** SuperSmoother(30) of the high-pass output.
- **Normalisation:** Peak = 0.991 × Peak[1], raised to |Filt| when
  larger; X = Filt / Peak (so |X| ≤ 1).
- **Quotients:** Q1 = (X + 0.85) / (0.85·X + 1); Q2 = (X + 0.40) /
  (0.40·X + 1).
- **Long entry:** Q1 crosses above 0.
- **Short entry:** Q2 crosses below 0.
- **Long exit:** Q2 crosses below 0 (the published sell signal).
- **Short exit:** Q1 crosses above 0 (the published buy signal).
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- John F. Ehlers, "The Quotient Transform", TASC August 2014
- TradeStation Traders' Tips (Aug 2014) with the published EasyLanguage:
  http://traders.com/documentation/feedbk_docs/2014/08/TradersTips.html

Paper only, no live execution.
