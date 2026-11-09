# Chikou Span Cross

Ichimoku's Chikou (lagging) span: today's closing price projected
back 26 periods. At bar i the span is compared against the price as
of 26 bars ago (`chikou_ref = close.shift(26)`). A cross of the
current close above / below that reference is exactly the Chikou
span crossing the price as of 26 bars ago — per Wikipedia, "If the
Chikou Span ... crosses the price in the bottom-up direction, that
is a buy signal. If the green line crosses the price from the
top-down, that is a sell signal."

## Rules

- Long: close crosses above the close 26 bars ago. Exit on the opposite cross (close below the close 26 bars ago).
- Short: close crosses below the close 26 bars ago. Exit on the opposite cross.
- ATR stop / trail from the risk layer also applies.

## Honest note

This is a 26-period momentum cross, nothing more: it is long
exactly when price is above where it was 26 bars ago and the
crossing just happened. It carries no cloud, Tenkan/Kijun, or
support/resistance confirmation — the full Ichimoku system is
deliberately NOT used here. Expect whipsaw in ranging markets: the
cross fires on every 26-bar momentum flip.

## Implementation note

The shared `strategies.base.ichimoku` helper computes chikou as
`close.shift(-26)` (the close plotted 26 bars forward), which uses
future data. It is NOT used here: this module only ever looks
backwards (`close.shift(+26)`), so there is no lookahead.

## Source

- Wikipedia — Ichimoku Kinko Hyo (Chikou span): https://en.wikipedia.org/wiki/Ichimoku_Kink%C5%8D_Hy%C5%8D

Paper only, no live execution.
