# Williams Fractal Breakout

Bill Williams fractal breakout with an Alligator filter: a 5-bar fractal (middle bar's high highest vs 2 bars each side, confirmed 2 bars late) sets the breakout level; long when the close crosses above the most recent up-fractal high while price is above the Alligator teeth and lips > teeth > jaw (awake, pointing up); short is the mirror; exit on the reverse fractal break.

## Rules

- Fractal: up-fractal when the middle bar has the highest high vs 2 bars each side; down-fractal the mirror on lows. Confirmed 2 bars late — the level is only known from the confirmation bar onward.
- Alligator: SMMA(13/8/5) of median price (jaw/teeth/lips), used unshifted (the classic Williams presentation shifts them forward 8/5/3 bars; this build does not, per spec).
- Long: close crosses above the most recent up-fractal high AND close above Alligator teeth AND lips > teeth > jaw.
- Short: close crosses below the most recent down-fractal low AND close below Alligator teeth AND lips < teeth < jaw.
- Exit: reverse fractal break (close crosses below the most recent down-fractal low for longs, above the most recent up-fractal high for shorts), plus ATR stop / trail from the batch-standard risk layer.
- Signals use only data through the current bar's close — no lookahead.

## Source

- Fractals gold trading (pro-scalper.com): https://www.pro-scalper.com/indicators/fractals-gold-trading

Paper only, no live execution.
