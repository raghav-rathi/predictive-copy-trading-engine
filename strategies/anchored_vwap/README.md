# Anchored VWAP

## Mechanism

VWAP is the cumulative typical price ((high + low + close) / 3)
times volume, divided by cumulative volume, measured from an
anchor bar. A session VWAP resets daily; an anchored VWAP
holds its anchor at a significant event — here, the most
recent swing pivot — and so tracks the average cost basis of
everyone who has traded since that pivot. Price above the
swing-low AVWAP means post-low buyers are on average in
profit; price below the swing-high AVWAP means post-high
buyers are on average underwater.

- **Pivot definition:** a bar j is a swing-high pivot when its
  high is the maximum high over the 20-bar window centred on
  j (10 bars each side); a swing-low pivot is the mirror with
  the minimum low.
- **Causality:** a pivot is only activated at bar j + 10,
  once its right-hand window is fully observed. No AVWAP value
  at bar i uses data beyond bar i. Before any pivot confirms,
  the series fall back to a VWAP cumulated from bar 0.
- **Long entry:** close crosses from below to above the AVWAP
  anchored at the last swing low, while that AVWAP is rising
  versus 5 bars ago.
- **Short entry:** mirror — close crosses from above to below
  the AVWAP anchored at the last swing high, while that AVWAP
  is falling versus 5 bars ago.
- **Exit:** the opposite cross of the same AVWAP.
- **Risk layer:** 2xATR stop, 2.5xATR trailing stop, 120-bar
  max hold, 1% risk per trade, 3x leverage cap.

## Source

Anchored VWAP (Brian Shannon; Investopedia anchored VWAP)
https://www.investopedia.com/terms/a/anchored-vwap.asp

Note on verification: a direct fetch of this page failed in
the build environment with a tool-side error (not a confirmed
404), so the link is retained as specified in the batch brief
rather than claimed as freshly verified; the AVWAP formula
itself (cumulative typical price x volume / cumulative
volume) is standard and corroborated by the VWAP sources
cited for the sibling strategy.

## Honest caveats

- The backtest (see BACKTEST.md) is a clear loser: -$5,543
  combined over 525 trades, 19.8% win rate, profit factor
  0.42–0.87 per coin. The cross-plus-slope rule does not
  demonstrate an edge on 1h crypto in this window.
- AVWAP is a slow cumulative average: after a strong move it
  sits far from price, so crosses require deep retraces, and
  the 10-bar pivot-confirmation delay means the anchor is
  always stale by the time it activates.
- Paper/backtest only. Nothing here touches live execution.
