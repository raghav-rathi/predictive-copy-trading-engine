# SMT Divergence

ICT Smart Money Technique divergence: when two correlated coins
disagree at their swing extremes, the one making the weaker extreme
is showing relative weakness — the divergence resolves when the
weaker coin breaks structure in the direction of the stronger coin's
bias.

## Rules

- **Pivots:** causal 5-bar pivots on both coins — a swing high at
  centre j iff h[j] is the max of h[j-2..j+2] (strictly above its
  left neighbour), a swing low iff l[j] is the min of l[j-2..j+2];
  recorded at the confirmation bar (centre+2), never at the centre.
- **Long entry (bullish SMT):** the traded coin prints a new swing
  low below its prior swing low while the reference coin's most
  recent swing low is HIGHER than its prior swing low, the two lows
  within 10 bars of each other (centre distance) — divergence armed;
  long on the first close above the traded coin's prior swing high
  (structure shift) within 20 bars of arming.
- **Short entry (bearish SMT):** the mirror — traded higher high,
  reference lower high, short on the first close below the traded
  coin's prior swing low within 20 bars.
- **Long exit:** an opposite bearish-SMT signal OR a close below the
  divergence swing low (invalidation).
- **Short exit:** an opposite bullish-SMT signal OR a close above
  the divergence swing high (invalidation).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

**Two-book structure:** the strategy trades a pair, so it runs as
two separate $10k books — BTC traded / ETH reference, and ETH traded
/ BTC reference. HYPE is excluded (no pair). `add_indicators` expects
a merged frame from `indicators.build_merged_frame(traded_df,
ref_df)` (inner join on `t`), not a single-coin frame — the same
pattern as pairs_spread's spread frame.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Sources

- The Inner Circle Traders, "ICT SMT Divergence":
  https://www.theinnercircletraders.com/ict-smt-divergence/
- XBTfx, "SMT Divergence Explained":
  https://xbtfx.com/blog/smt-divergence-explained-meaning-bullish-and-bearish/

Paper only, no live execution.
