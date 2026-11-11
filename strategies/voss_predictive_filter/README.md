# Voss Predictive Filter

John Ehlers' Voss Predictive Filter ("A Peek Into The Future", TASC
August 2019): a 2-pole band-pass filter isolates the cyclic component
around a 20-bar cycle, then the Voss predictor — a negative-group-delay
filter — advances its phase, so its peaks and zero-crossings appear
before the corresponding events in the band-pass output.

## Rules

- **Band-pass line:** 2-pole filter, period 20, bandwidth 0.25
  (`Filt = 0.5*(1-S1)*(Close − Close[2]) + F1*(1+S1)*Filt[1] − S1*Filt[2]`).
- **Voss line:** `Voss = 6*Filt − SumC`, where `SumC` is the
  order-9 weighted sum of past Voss values (predict 3, order 9).
- **Long entry:** Voss crosses above the band-pass line, gated by
  ADX(14) < 25 (stay out when the trend is strong).
- **Short entry:** Voss crosses below the band-pass line, same ADX gate.
- **Long exit:** Voss crosses below the band-pass line.
- **Short exit:** Voss crosses above the band-pass line.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close. The Voss line is a phase advance, not a forecast: it
does not see future prices.

## Sources

- John F. Ehlers, "A Peek Into The Future", TASC August 2019
- FMZ strategy writeup with the published recursion: https://www.fmz.com/strategy/427275
- Wealth-Lab Traders' Tip (TASC Aug 2019) with the ADX rule and
  `VossPredictor.Series(Close, 20, 3)` / `BandPass.Series(Close, 20)`:
  http://www2.wealth-lab.com/wl5wiki/Print.aspx?Page=TASCAug2019
- TradeStation Traders' Tips (TASC Aug 2019) EasyLanguage source:
  http://traders.com/Documentation/FEEDbk_docs/2019/08/TradersTips.html

Paper only, no live execution.
