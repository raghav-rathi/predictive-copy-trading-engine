# Fibonacci Retracement

Fibonacci retracement pullback (golden zone) on 5-bar fractal pivots. Swings are consecutive fractal pivots; an impulse leg A→B must be ≥ 1.0x ATR(14). In an uptrend (B is a swing high above A), wait for a pullback into the 38.2%–61.8% retracement zone of A→B; enter long on the close of the first green candle that closes in or above the zone (the signal candle), only on the first touch of the zone. Target is the old high B — exit long at a close ≥ B. A close beyond A kills the setup (the harness 2xATR stop is the enforced stop). Short is the mirror image in downtrends.

## Rules

- Long: uptrend swing (A low → B high, leg ≥ 1.0x ATR(14)); pullback touches the zone (low ≤ 38.2% level); enter on the first green candle closing in or above the zone (close ≥ 61.8% level), once per swing, only while the close is still between A and B.
- Short: downtrend swing; pullback touches the zone (high ≥ 38.2% level); enter on the first red candle closing in or below the zone, once per swing.
- Exit long: close ≥ B (old high) or close below A (invalidation). Exit short is the mirror.
- A new pivot low after B is the pullback itself and never flips the swing; a newer same-direction swing replaces the active one only while it is untouched; once the zone is touched the swing is locked so the armed setup's levels cannot shift; opposite-direction swings only activate when no swing is active.
- Pivots are 5-bar local extrema with a minimum 0.9x ATR(14) swing, usable only 2 bars after the extreme bar — no lookahead.

## Source

- Fibonacci retracement pullback (TradingWalk): https://tradingwalk.com/fibonacci-tips

Paper only, no live execution.
