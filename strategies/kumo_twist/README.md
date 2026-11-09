# Ichimoku Kumo Twist

The cloud changing colour: Senkou Span A crossing Senkou Span B.

- Senkou Span A = (Tenkan-sen(9) + Kijun-sen(26)) / 2.
- Senkou Span B = (highest high + lowest low over 52 bars) / 2.

## Rules

- Long: Senkou Span A crosses above Senkou Span B (cloud twists bullish). Exit on a twist down.
- Short: Senkou Span A crosses below Senkou Span B (cloud twists bearish). Exit on a twist up.
- ATR stop / trail from the risk layer also applies.

## Causality — NO forward displacement

Textbook Ichimoku plots both spans **26 bars ahead** of the bar they
are computed from, so the cloud visible at bar i was computed from
data through bar i−26. This strategy does NOT use the displaced
(plotted) values. The spans here are evaluated at bar i from data
through bar i — the cloud as known at bar i, with no 26-bar shift in
either direction. A twist is therefore a cross of the two current,
causal span values. Using the displaced spans would mean trading a
26-bar-stale cloud; using a forward-shifted span would be lookahead.
Neither is done here. The shared `strategies.base.ichimoku` helper's
shifted Senkou columns are not used; the spans are computed unshifted
in `indicators.py`, and a test (`test_spans_are_unshifted`) proves the
stored Span B differs from the displaced value.

## Source

- BabyPips — Ichimoku Kinko Hyo (Kumo twist section): https://www.babypips.com/learn/forex/ichimoku-kinko-hyo

Paper only, no live execution.
