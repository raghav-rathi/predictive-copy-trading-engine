# Keltner Channel + RSI — Calibration

## Parameter choices

Keltner EMA(20), ATR(10), multiplier 1.5 is Raschke's modern channel form (not Keltner's original SMA/range form), and RSI(14) is Wilder's standard. The [50,75]/[25,50] bands deliberately exclude both the dead zone near 50-without-breakout and the overbought/oversold extremes. Warmup 30 bars covers EMA(20) and RSI(14) with margin. Risk is the batch standard.

## Sensitivity note

No parameter sweep was run on this window; EMA(20)/ATR(10)/1.5× and RSI(14) with [50,75]/[25,50] bands are the textbook Raschke/Wilder settings, chosen a priori. Widening the channel or narrowing the RSI band would cut trades but also cut the follow-through trades that pay; narrowing the channel would add chop entries. The all-legs-losing pattern points at the thesis, not the knobs.

## Verdict

LOSER on all three legs. Combined −$5,665 across 660 trades (−$8.58 expectancy, the worst per-trade expectancy in the batch). BTC −$2,852 (Sharpe −2.05) and ETH −$2,284 lead the losses; even HYPE loses. The RSI filter trims the worst blow-offs (verified in tests: an overbought breakout is blocked) but the remaining breakouts still mean-revert more often than they follow through. Channel-breakout + momentum-band confirmation is not an edge on 1h crypto in this window.
