# StatOasis Rule 5: Double-Overbought Short Fade

StatOasis tested five AI-generated rules on SPY. Rule 5 is the
only one that survived out-of-sample validation — but only just,
and only out-of-sample: it lost −$720 in-sample and made +$2,591
out-of-sample at a 75.0% win rate (Monte Carlo percentile 95.5).
This strategy is a fade test on 1h crypto, not a star. Say so
plainly; the backtest below is the verdict, not the marketing.

## Rule

**SHORT** when all three hold on the same bar:

```
RSI(14) > 70
Williams %R(14) > -10   (close within 10% of the 14-bar high)
SMA(100) falling        (SMA100[i] < SMA100[i-1])
```

**LONG mirror (builder-added)** when all three invert:

```
RSI(14) < 30
Williams %R(14) < -90   (close within 10% of the 14-bar low)
SMA(100) rising
```

## Exit

Fixed **5-bar hold** (5h on 1h bars — the daily rule's 5-bar hold
adapted 1:1 in bars). A bar-count state machine fires the exit on
the 5th bar after entry; the harness executes at the next bar's
open. No signal-level stop or target. The harness's 2×ATR stop and
5-bar max hold are backstops.

## Risk

Roomy 2×ATR stop (the fixed hold, not the stop, should normally
end the trade), no trail, no target, 5-bar max hold, 1% risk per
trade, 3× leverage cap. WARMUP = 120 bars (SMA100 + margin).

Source: StatOasis, "Can AI Build a Profitable Trading Strategy?
5 Rules Tested"
(https://statoasis.com/overfit/research/ai-strategy-validation).
