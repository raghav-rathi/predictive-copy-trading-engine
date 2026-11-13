# RSI Hidden Divergence

RSI(14) hidden divergence is the trend-continuation form of divergence
(Wilder's RSI, 1978; the "positive/negative RSI reversal" in the
standard literature): in an uptrend, price pulls back to a *higher*
swing low while RSI dips to a *lower* low — momentum is resetting
while price holds higher ground, so the trend is expected to continue
up. The mirror image (lower swing high, higher RSI high) continues a
downtrend. Regular divergence (lower price low + higher RSI low) is
the reversal setup and is deliberately not traded here.

## Rules

- **Long entry:** bullish hidden divergence confirmed — price makes a
  higher swing low while RSI makes a lower low at that pivot.
- **Short entry:** bearish hidden divergence confirmed — price makes
  a lower swing high while RSI makes a higher high at that pivot.
- **Long exit:** RSI crosses below 50.
- **Short exit:** RSI crosses above 50.
- Swing pivots are 5-bar (2 bars each side). A pivot at bar i is
  confirmed at bar i+2, so the entry fires on the confirmation bar —
  two bars after the pivot prints — and never before.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the RSI-50 cross. Max hold 120 bars.
- Parameters are the canonical defaults (RSI 14, 5-bar pivots, exit
  at RSI 50); nothing was tuned to this window.

All computation is causal: a signal on bar i uses only data through
bar i's close. The pivot columns mark the pivot bar itself, but the
signal loop only acts on a pivot at its confirmation bar (i+2).

## Source

- J. Welles Wilder Jr., *New Concepts in Technical Trading Systems*
  (1978), RSI; divergence / RSI-reversal taxonomy per Investopedia:
  https://www.investopedia.com/terms/r/rsi.asp

Paper only, no live execution.
