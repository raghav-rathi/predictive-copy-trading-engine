# Keltner Channel + MACD Combo

A volatility-expansion breakout (close above the upper Keltner
band) confirmed by MACD momentum — the Raschke-style channel
trade with Appel's MACD as the agreement filter. The idea: the
channel break says price is expanding, the MACD histogram says
momentum agrees, so the break is a trend start rather than a
one-bar spike.

## Rule (long)

```
close breaks above the upper Keltner band (20, 1.5 x ATR(10))
    — transition only: prior close at/below the prior upper band
AND MACD(12, 26, 9) histogram > 0 on the same bar
```

- **Exit long:** close back inside the channel (close < upper
  band) OR the MACD histogram turning negative (hist < 0).
- **Short mirror:** close breaks below the lower band while the
  histogram is negative; exit on a close back inside the channel
  (close > lower band) OR the histogram turning positive.
- **Flip:** an opposite setup while in a position exits and
  enters the other side on the same bar (a short breakout bar is
  by construction also a close back inside the channel for a
  long, so the flip follows from the exit rule).

## 1h scaling (documented)

- Keltner(20, 1.5×ATR(10)) and MACD(12, 26, 9) are used as
  published — no rescaling; on 1h bars the 20-bar EMA is a
  ~20-hour midline and the channel is correspondingly tight.
- Entries execute at the next bar's open per the house
  convention, so a one-bar breakout is entered after the break
  bar has already closed.

## Honest flag: the dual-agreement filter can agree too late

This is the known failure mode to watch in the verdict. The
breakout bar is usually the fastest bar of the move; requiring
the MACD histogram to also be positive on that same bar means
the filter agrees only after momentum has already turned — and
on 1h crypto the close is very often back inside the channel on
the very next bar, which is the exit. The backtest bears this
out: ~90% of trades exit on the signal (not the stop), the
strategy trades 1,084 times in eight months, and it loses on
all three coins. See BACKTEST.md.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level
channel-re-entry exit is the real stop), no trail, no target,
120-bar (~5-day) max hold, 1% risk per trade, 3× leverage cap.
WARMUP = 40 bars (MACD signal/histogram needs ~34 bars to
seed; 40 covers the Keltner EMA(20) as well).

Source: Linda Raschke & Laurence Connors, *Street Smarts*
(1995), Keltner Channel chapter; MACD per Gerald Appel —
https://www.tradingview.com/scripts/keltner/ (reference only;
implemented from the book rules above).
