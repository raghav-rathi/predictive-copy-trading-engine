# Order Flow Imbalance

## Mechanism

A footprint chart splits each bar's volume into aggressive
buys (market orders lifting the offer) and aggressive sells
(market orders hitting the bid); bar delta is buys minus
sells, and cumulative delta chains it across a session.
True delta needs tick-level bid/ask classification, which 1h
OHLCV bars do not carry — so this strategy uses the standard
bar-delta **proxy** from the bar's own price travel:

    delta = volume * (close - open) / max(high - low, eps),
    clipped to [-volume, volume]

A bar closing at its high scores +volume (all volume read as
buying pressure); a bar closing at its low scores -volume; a
doji scores 0. The imbalance is the 5-bar rolling sum of
delta divided by the 5-bar rolling sum of volume, bounded in
[-1, 1] by construction: +1 means every bar in the window
closed at its high, -1 the mirror.

- **Long entry:** imbalance crosses above +0.25 while close
  is above EMA(20) — one-sided buying pressure confirmed by
  price sitting above its short trend.
- **Short entry:** imbalance crosses below -0.25 while close
  is below EMA(20).
- **Exit:** imbalance crosses back through 0 — the one-sided
  pressure is gone.
- **Risk layer:** 2xATR stop, 2.5xATR trailing stop, 120-bar
  max hold, 1% risk per trade, 3x leverage cap.

## Source

Footprint charts and cumulative delta (order-flow delta:
aggressive buys minus aggressive sells)
https://nordfx.com/useful-articles/footprint-charts-cumulative-delta-order-flow-trading

This source explains the mechanism (footprint bid/ask split,
delta as net aggression, cumulative delta as its running
total); the bar-delta proxy itself is this strategy's
adaptation to OHLCV-only data, not a claim about the source.

## Honest caveats

- The backtest (see BACKTEST.md) is a clear loser: -$10,996
  combined over 1,424 trades, 30.5% win rate. The proxy fires
  constantly (about 2 trades per coin per day) and mostly
  churns: fees alone are $9,476.
- The proxy is weak by construction: (close - open) / range
  measures where a bar closed inside its range, not who
  crossed the spread. A bar can close near its high on
  short-covering or thin volume with no aggressive buying
  behind it.
- Paper/backtest only. Nothing here touches live execution.
