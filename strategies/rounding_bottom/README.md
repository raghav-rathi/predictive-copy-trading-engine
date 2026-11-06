# Rounding Bottom

Rounding bottom / saucer (Edwards & Magee): a 60-bar U-shape with the trough
in the middle third of the window, left and right rims within 2% of each
other, the trough at least 3x ATR(14) below the lower rim, and a 10-bar SMA
slope that falls over the first half of the window and rises over the second.
The neckline is the left-rim level. The rounding-top mirror trades the short
side. Both directions fired in the backtest (714 long signals, 775 short
signals across the three coins).

## Rules

- Long: close above the prior-bar rounding-bottom neckline with volume above
  its 20-bar average, within 20 bars of the pattern detection.
- Short: close below the prior-bar rounding-top neckline with volume above
  its 20-bar average, within 20 bars of the pattern detection.
- Exit long: close back below the neckline (within 120 bars of detection).
  Exit short is the mirror.
- Neckline, pattern age and volume average are all shifted by 1, so the close
  is never compared with a neckline computed from the current bar.

## Source

- Rounding Bottom / Saucer (Edwards & Magee): https://www.indiainfoline.com/knowledge-center/online-share-trading/what-is-the-rounding-bottom-patterns

Paper only, no live execution.
