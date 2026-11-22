# StatOasis Rule 4: Multi-Indicator Momentum

StatOasis Rule 4 from "Can AI Build a Profitable Trading
Strategy? 5 Rules Tested" — one of only 2 of 5 AI-generated
rules to clear the 95th Monte Carlo percentile on SPY daily
out-of-sample (+$31,954, 69.2% win rate, percentile 96.7).
Implemented exactly as written, adapted from daily SPY to 1h
crypto bars.

## Mechanism

**LONG** when all four hold simultaneously:

- RSI(14) > 55
- Stochastic %K(14, smooth 3) > 50
- Williams %R(14) > −50
- 120h return > 1% (the source's 5-day return, on 1h bars)

**Exit:** fixed 10-bar time exit (10 hours here, 10 days in the
source). There is **no indicator exit** — the position is held
for exactly 10 bars and then closed, whatever the oscillators
say. The exit is enforced twice: by the bar-count state machine
in signals.py and by `max_hold_bars=10` in the harness.

**SHORT** is a builder-added mirror of the long-only source:
RSI < 45 AND %K < 50 AND %R < −50 AND 120h return < −1%,
same 10-bar time exit.

## Risk

2xATR(14) stop as catastrophic protection only; trailing is
OFF (a trail would fight the fixed-hold thesis by cutting
winners short before the 10 bars elapse); no target. 1% risk
per trade, 3x leverage cap. WARMUP = 150 bars (120h return
lookback + spin-up).

## What the source study actually concluded

Rule 4 was the best of the five AI rules — and still lost to
buy-and-hold SPY by more than $55,000 out-of-sample, and none
of the 2,068 optimizer variants beat buy-and-hold either. The
study's verdict is "impressive backtests, not guaranteed
edges." This implementation inherits that caution: the rule is
a momentum-timing test, not a claim of edge.

Source: StatOasis — "Can AI Build a Profitable Trading
Strategy? 5 Rules Tested" (Rule 4)
(https://statoasis.com/overfit/research/ai-strategy-validation).
