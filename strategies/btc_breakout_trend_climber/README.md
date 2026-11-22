# BTC Breakout Trend Climber

A breakout trend system from a QuantConnect community backtest
(reported Sharpe 2.42, long-only in the source). The source is a
BTC trend strategy; it is run here on BTC, ETH and HYPE, mirrored
for shorts.

## Mechanism

LONG entry on either breakout leg (an OR):

1. **25-day Donchian breakout** — close crosses above the highest
   high of the prior 600 bars (25 days on 1h bars). The level is
   computed from the prior 600 bars only (shifted by one), so the
   breakout bar's own high can never set the level it breaks.
2. **Bollinger Band breakout** — close crosses above the upper
   Bollinger Band (50-period, 2.1 sigma, **EMA-based mid** — the
   source uses an EMA mid, unlike the SMA mid in
   `strategies.base.bollinger`).

SHORT entry is the mirror: close crosses below the prior-600-bar
lowest low, or below the lower Bollinger Band.

## Exits

- Opposite breakout: a short breakout while long exits the long
  (and opens the short — the harness flips), and vice versa.
- ATR-staged stop/trail (see risk.py): 3.5xATR(10) hard stop with
  an 11.0xATR(10) chandelier trail. There is no fixed target and
  no max hold — the source exits only on the stop/trail.

## Risk

3.5xATR(10) stop, 11.0xATR(10) trail, no target, no max hold, 1%
risk per trade, 3x leverage cap. WARMUP = 610 bars (600-bar
Donchian + margin).

Source: QuantConnect community backtest — BTC Breakout Trend
Climber
(https://www.quantconnect.com/terminal/cache/embedded_backtest_ad553ee3018fa48c5a0395a33ba8b2dd.html).
