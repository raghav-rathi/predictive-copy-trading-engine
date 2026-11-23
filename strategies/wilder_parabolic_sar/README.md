# Wilder Parabolic SAR system

Wilder's Parabolic SAR (1978): a trailing stop that accelerates
toward price as the trend extends, flipping the position the
moment price penetrates it. LONG while price is above the SAR,
SHORT while below it — the flip closes one side and opens the
other.

## Rule

```
AF starts at 0.02, grows by 0.02 per new extreme, capped at 0.20
LONG:  SAR = SAR_prev + AF * (EP - SAR_prev), EP = highest high
       SAR never exceeds the lowest low of the prior two bars
       flip to SHORT when low < SAR (new SAR = old EP)
SHORT: mirror image
```

- **Entry:** the flip itself. The system is always in the market
  once entered — there is no flat state in Wilder's original.
  (One exception: bar 0 is seeded LONG but emits no entry; the
  first trade is the first genuine flip.)
- **Exit:** the flip itself. The 2×ATR(14) harness stop is a
  backstop only.
- **No trail, no target:** the SAR *is* the trailing stop.

## Why this build exists: raw PSAR, no filter

This is the raw PSAR system **WITHOUT** the MACD agreement
filter used by the existing `psar_macd` strategy — that is the
point of this build (isolate PSAR's own edge). The backtest
answer is that on 1h crypto there is no surviving edge: the
unfiltered system loses on all three coins (see BACKTEST.md),
gross-positive before fees but fee-negative after them. The
MACD filter in `psar_macd` exists precisely because PSAR
whipsaws in chop — this build is the evidence for why.

## 1h scaling (documented)

- Wilder designed PSAR on daily bars. On 1h bars it flips far
  more often — a flip every ~12 bars in this window, 1,466
  trades across three coins in eight months.
- Each flip pays the round-trip cost twice (exit + re-entry),
  so transaction costs dominate the result at this turnover.

## Honest flag: whipsaw is the mechanism, not a bug

PSAR assumes trending markets. In the sideways/choppy stretches
that dominate 1h crypto, the SAR flips on every counter-trend
wiggle and the system bleeds. A -52.5% max drawdown on BTC is
the honest outcome of running an always-in trend system through
a choppy downtrend — not a parameter error.

## Risk

2×ATR(14) harness stop as a backstop (the SAR flip is the real
exit), no trail, no target, 336-bar (~14-day) max hold, 1% risk
per trade, 3× leverage cap. WARMUP = 20 bars.

Source: J. Welles Wilder, *New Concepts in Technical Trading
Systems* (1978) — https://en.wikipedia.org/wiki/Parabolic_SAR
