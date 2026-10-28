# PPO Signal Cross — Calibration

## Parameter choices

PPO(12,26,9) mirrors MACD(12,26,9) exactly, so the two strategies are directly comparable: the only difference is the price normalisation and the trigger (signal cross vs zero cross). That comparison is the point — and it lands against the signal cross. Warmup 40 bars covers EMA(26) plus the signal EMA with margin. Risk is the batch standard.

## Sensitivity note

No parameter sweep was run on this window; PPO(12,26,9) is the textbook setting, chosen a priori. A longer signal EMA would cut trade count but also delay the exits that cap losses; a shorter one would add whipsaws. The failure is structural (cross frequency in chop), not a parameter miss — no plausible EMA tweak turns 1,221 whipsaw trades into an edge, and tuning on this window would be overfitting.

## Verdict

LOSER — the worst in this batch. Combined −$7,752 across 1,221 trades (−$6.35 expectancy), with BTC down −48.6% of starting equity and a −51.2% max drawdown. The PPO normalisation is elegant but irrelevant here: dividing by price does not fix the signal cross's core defect, which is firing on every minor oscillator wiggle. Over 1,200 trades, the verdict is not ambiguous — this trigger loses on 1h crypto.
