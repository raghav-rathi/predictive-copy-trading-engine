# Gap Fill Fade

Classic gap-fill mean reversion: when a 1h bar gaps away from
the prior close, fade the gap — buy the gap down, short the
gap up — expecting price to fill back to the prior close.

## Rule

```
Gap: gap = open[i] - close[i-1]; a gap fires when
  |gap| > 0.5 * ATR(14)   (strict — exactly 0.5 ATR is NOT a gap)
LONG on a gap down (gap < -0.5 * ATR), SHORT on a gap up.
  One fade per gap, fired on the gap bar itself.
EXIT long when close >= prev_close (the gap is filled),
  or on an opposite gap signal (gap up).
EXIT short when close <= prev_close, or on an opposite gap
  signal (gap down).
```

- **The gap is visible at the open, known by the close:**
  the signal fires on the gap bar and executes at the next
  bar's open per the house convention.
- **One fade per gap:** while a fade is held, further gap
  bars do not re-enter. A fill that already happened on the
  gap bar itself does not exit the trade — the position only
  exists from the next bar's open, so fill exits are checked
  from the bar after entry onward.
- **No target:** the fill exit is the target. The risk layer
  adds a 2×ATR(14) stop and a 24-bar max hold.
- **Max hold:** 24 bars (~1 day on 1h).

## Honest flag: gaps barely exist on 1h crypto

Crypto trades 24/7, so there is no overnight session break
to produce gaps. A ≥0.5 ATR open-to-prior-close gap fires
only 25 times across three coins in eight months (~1 per coin
per month). The backtest is a 25-trade sample — far too small
to support any claim about the edge. See BACKTEST.md.

## 1h scaling notes

- On daily equities, gaps are a session-break phenomenon and
  fill rates are a real statistic. On 1h crypto, a "gap" is
  just one hourly jump among 6,111 — usually a fast move that
  already happened, not a dislocation waiting to fill.
- The exit mix shows it: only 9 of 25 trades exit on a fill;
  10 hit the stop and 6 run out the 24-bar clock. The fill
  usually does not arrive within a day, if it arrives at all.

## Risk

2×ATR(14) harness stop, no trail, no target, 24-bar (~1-day)
max hold, 1% risk per trade, 3× leverage cap. WARMUP = 30
bars (ATR(14) seeding plus margin).

Source: Gap-fill mean reversion (Bulkowski, *Encyclopedia of
Chart Patterns*) (https://thepatternsite.com/GaugingGaps.html).
