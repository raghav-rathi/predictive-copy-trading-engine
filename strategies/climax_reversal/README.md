# Climax Reversal

Wyckoff buying/selling climax reversal: trade the exhaustion bar.
Wyckoff's law of effort vs result says volume is the effort and the
price move is the result — when huge effort produces no result, the
trend is about to turn.

## Rules

- **Buying climax (short signal):** new 20-bar high AND volume >
  2x the trailing 20-bar mean volume AND close in the LOWER third
  of the bar's range. Buyers pushed to a new high on huge volume
  but the close fell back: supply absorbed the buying.
- **Selling climax (long signal):** new 20-bar low AND volume >
  2x the trailing 20-bar mean volume AND close in the UPPER third
  of the bar's range. Sellers pushed to a new low on huge volume
  but the close recovered: demand absorbed the selling.
- **Long exit:** the opposite climax (buying climax).
- **Short exit:** the opposite climax (selling climax).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The volume mean uses the previous 20 bars (so the current bar's own
spike does not dilute the comparison); the 20-bar high/low includes
the current bar (a new extreme is only known at the close). All
computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Richard D. Wyckoff, the Wyckoff method — buying climax (BC) and
  selling climax (SC), law of effort vs result; Tom Williams,
  *Master the Markets* (VSA climax bars):
  https://patternswizard.com/wyckoff-method/

Paper only, no live execution.
