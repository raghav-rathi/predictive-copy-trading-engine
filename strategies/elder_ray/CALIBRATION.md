# Elder Ray — Calibration

**Shipped:** Bull/Bear Power vs EMA(13); long on rising EMA + negative
turning-up Bear Power; exit on zero cross against the trade; 2xATR
stop, 3xATR trail.

**What the numbers say:** −$5,347 combined, BTC −40.7% at PF 0.53.
The single-bar turn detection fires on noise — most "exhaustion"
reads are just 1h jitter. The rising-EMA gate doesn't filter because
13-bar EMA whipsaws on 1h.

**Next experiment (only if revisited):** smooth Bear Power with a
3-bar average before turn detection and require 5-bar EMA slope. Two
changes, both aimed at the same defect: the trigger is too fast for
the timeframe.

**Do not:** port to 1h with daily-calibrated instincts — Elder's
setups assume daily bars where a "turn" means something.
