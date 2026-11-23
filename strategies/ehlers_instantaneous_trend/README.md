# Ehlers Instantaneous Trendline

John Ehlers' Instantaneous Trendline (Rocket Science for
Traders, 2001): a near-zero-lag recursive trend filter. Trade
price against the line itself — above a rising line is an
uptrend, below a falling line is a downtrend.

## Rule (long)

```
alpha = 0.07
IT[i] = (a - a^2/4)*C[i] + 0.5*a^2*C[i-1] - (a - 0.75*a^2)*C[i-2]
      + 2*(1-a)*IT[i-1] - (1-a)^2*IT[i-2]
LONG when C > IT AND IT is rising (IT[i] > IT[i-1])
```

- **Short mirror:** C < IT and IT falling.
- **Exit long:** close back through the trendline (C <= IT),
  OR the trendline turns against the position (IT falling).
  Exit short on the mirror.
- **Entries are transition-only:** a position opens only on
  the bar where the condition first becomes true (after being
  false the prior bar), never re-entered while the condition
  merely persists.
- **Flip:** an opposite-side transition while in a position
  flips it (exit + opposite entry on the same bar); a plain
  exit only closes the position.

## 1h scaling (documented)

- **alpha = 0.07 is the book's 7-day-equivalent constant ported
  unscaled to 1h.** Ehlers calibrated alpha = 0.07 for daily
  bars (roughly a 7-day cycle); we use it unchanged on hourly
  bars. That is a documented choice, not a tuned one — the
  filter is therefore much faster relative to the bar than in
  the daily original, and it hugs price closely. See
  CALIBRATION.md.
- Seeding: IT[0] = C[0], IT[1] = C[1] per spec. The filter
  settles within a handful of bars; WARMUP = 30 bars makes the
  seed irrelevant to traded bars.
- A useful property of the coefficients: they sum to 1, so the
  filter tracks a linear price ramp exactly (zero lag on a
  straight trend) — verified by unit test.

## Honest flag: a near-zero-lag line whipsaws on 1h crypto

Because the trendline hugs price, price crosses it constantly
on noisy 1h bars — the system fires ~750 trades per coin in
eight months (see BACKTEST.md) and is almost always in a
position. The near-zero lag that makes the line attractive on
daily bars becomes a liability here: every wiggle is a
crossing, every crossing is a round trip at 0.055% per side.
The mechanism works exactly as specified — the losses are the
strategy's, not an implementation bug.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level
cross-back and turn exits are the real exits), no trail, no
target, 168-bar (~7-day) max hold, 1% risk per trade, 3×
leverage cap. WARMUP = 30 bars.

Source: John Ehlers, Rocket Science for Traders (2001),
Instantaneous Trendline chapter
(https://www.mesasoftware.com/papers/).
